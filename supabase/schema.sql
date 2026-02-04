-- Sift Retail AI - Supabase Database Schema
-- Run this in your Supabase SQL Editor to create the required tables

-- ============================================
-- TENANTS TABLE
-- Stores retailer/store information
-- ============================================
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast tenant lookups
CREATE INDEX IF NOT EXISTS idx_tenants_created_at ON tenants(created_at);

-- ============================================
-- PRODUCTS TABLE
-- Stores product data (hard data: price, stock, images)
-- ============================================
CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,  -- Format: {tenant_id}_{external_id}
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    external_id TEXT NOT NULL,
    name TEXT NOT NULL,
    slug TEXT,
    sku TEXT,
    price DECIMAL(10,2) DEFAULT 0,
    regular_price DECIMAL(10,2) DEFAULT 0,
    sale_price DECIMAL(10,2),
    stock_status TEXT DEFAULT 'instock',
    stock_quantity INTEGER,
    description TEXT,
    short_description TEXT,
    categories TEXT[] DEFAULT '{}',
    image_url TEXT,
    permalink TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast product queries
CREATE INDEX IF NOT EXISTS idx_products_tenant_id ON products(tenant_id);
CREATE INDEX IF NOT EXISTS idx_products_external_id ON products(external_id);
CREATE INDEX IF NOT EXISTS idx_products_categories ON products USING GIN(categories);

-- ============================================
-- SEARCH LOGS TABLE
-- Tracks user searches for ROI analytics
-- ============================================
CREATE TABLE IF NOT EXISTS search_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    query TEXT NOT NULL,
    results_count INTEGER DEFAULT 0,
    session_id TEXT,
    converted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_search_logs_tenant_id ON search_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_search_logs_query ON search_logs(query);

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- Enable for production multi-tenant security
-- ============================================

-- Enable RLS on all tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_logs ENABLE ROW LEVEL SECURITY;

-- For now, allow all operations from service role
-- In production, you'd want more restrictive policies
CREATE POLICY "Allow all for service role" ON tenants
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role" ON products
    FOR ALL USING (true);

CREATE POLICY "Allow all for service role" ON search_logs
    FOR ALL USING (true);

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert a sample tenant
INSERT INTO tenants (id, name, config)
VALUES ('vanleeuwen', 'Van Leeuwen Ice Cream', '{"woocommerce_url": "https://vanleeuwenicecream.com"}')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- ANALYTICS VIEWS (Optional)
-- ============================================

-- View for daily search stats
CREATE OR REPLACE VIEW daily_search_stats AS
SELECT
    tenant_id,
    DATE(created_at) as date,
    COUNT(*) as total_searches,
    COUNT(DISTINCT query) as unique_queries,
    COUNT(*) FILTER (WHERE results_count = 0) as zero_result_searches,
    COUNT(*) FILTER (WHERE converted = true) as conversions
FROM search_logs
GROUP BY tenant_id, DATE(created_at)
ORDER BY date DESC;

-- View for top queries per tenant
CREATE OR REPLACE VIEW top_queries AS
SELECT
    tenant_id,
    LOWER(query) as query,
    COUNT(*) as search_count,
    AVG(results_count) as avg_results
FROM search_logs
GROUP BY tenant_id, LOWER(query)
ORDER BY search_count DESC;
