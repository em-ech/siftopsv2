"use client";

import { useState, useRef, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { siftChat, type ChatMessage, type SiftSearchResult } from "@/lib/api";

interface ChatPanelProps {
  onProductsFound?: (products: SiftSearchResult[]) => void;
}

interface Message extends ChatMessage {
  products?: SiftSearchResult[];
  isLoading?: boolean;
}

export function ChatPanel({ onProductsFound }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I'm your Van Leeuwen ice cream expert. Ask me anything about our flavors, ingredients, or help finding the perfect treat!",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");

    // Add user message
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    // Add loading indicator
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", isLoading: true },
    ]);
    setIsLoading(true);

    try {
      // Get chat history (exclude loading message)
      const history: ChatMessage[] = messages
        .filter((m) => !m.isLoading)
        .map((m) => ({ role: m.role, content: m.content }));

      const response = await siftChat(userMessage, history);

      // Remove loading and add response
      setMessages((prev) => [
        ...prev.filter((m) => !m.isLoading),
        {
          role: "assistant",
          content: response.response,
          products: response.products,
        },
      ]);

      // Notify parent of found products
      if (onProductsFound && response.products.length > 0) {
        onProductsFound(response.products);
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev.filter((m) => !m.isLoading),
        {
          role: "assistant",
          content:
            "Sorry, I'm having trouble connecting right now. Please make sure the backend server is running on http://localhost:8000",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const suggestedQuestions = [
    "What's your best vegan option?",
    "Something refreshing for summer",
    "What flavors have chocolate?",
    "Any nut-free options?",
  ];

  return (
    <div className="flex flex-col h-[600px] bg-white border border-[var(--color-border)] rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-[var(--color-background-alt)] border-b border-[var(--color-border)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[var(--color-accent)] flex items-center justify-center">
            <svg
              className="w-5 h-5 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
          <div>
            <h3 className="font-medium text-sm">Sift AI Assistant</h3>
            <p className="text-xs text-[var(--color-text-muted)]">
              Powered by RAG - Only real products, zero hallucinations
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] ${
                message.role === "user"
                  ? "bg-[var(--color-primary)] text-white"
                  : "bg-[var(--color-background-alt)]"
              } rounded-lg px-4 py-3`}
            >
              {message.isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-[var(--color-text-muted)] rounded-full animate-bounce" />
                    <span
                      className="w-2 h-2 bg-[var(--color-text-muted)] rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    />
                    <span
                      className="w-2 h-2 bg-[var(--color-text-muted)] rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                  </div>
                  <span className="text-sm text-[var(--color-text-muted)]">
                    Thinking...
                  </span>
                </div>
              ) : (
                <>
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                  {/* Product recommendations */}
                  {message.products && message.products.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-[var(--color-border)]">
                      <p className="text-xs font-medium text-[var(--color-text-muted)] mb-2">
                        Recommended Products:
                      </p>
                      <div className="space-y-2">
                        {message.products.slice(0, 3).map((product) => (
                          <Link
                            key={product.id}
                            href={`/product/${product.id}`}
                            className="flex items-center gap-3 p-2 bg-white rounded border border-[var(--color-border)] hover:border-[var(--color-accent)] transition-colors"
                          >
                            {product.image_url && (
                              <div className="relative w-12 h-12 flex-shrink-0">
                                <Image
                                  src={product.image_url}
                                  alt={product.name}
                                  fill
                                  className="object-cover rounded"
                                />
                              </div>
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium truncate">
                                {product.name}
                              </p>
                              <p className="text-xs text-[var(--color-text-muted)]">
                                ${typeof product.price === 'number' ? product.price.toFixed(2) : parseFloat(String(product.price)).toFixed(2)}
                              </p>
                            </div>
                            <span className="text-xs text-[var(--color-accent)]">
                              {Math.round(product.score * 100)}% match
                            </span>
                          </Link>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-[var(--color-text-muted)] mb-2">
            Try asking:
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q) => (
              <button
                key={q}
                onClick={() => setInput(q)}
                className="text-xs px-3 py-1.5 bg-[var(--color-background-alt)] hover:bg-[var(--color-border)] rounded-full transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="p-4 border-t border-[var(--color-border)]"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about flavors, ingredients, recommendations..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-[var(--color-border)] focus:border-[var(--color-primary)] focus:outline-none rounded-lg disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary)]/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
}
