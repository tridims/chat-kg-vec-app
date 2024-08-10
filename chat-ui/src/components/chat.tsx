"use client";

import React, { useState, useEffect, useCallback } from "react";
import { nanoid } from "nanoid";
import {
  SearchIcon,
  SettingsIcon,
  SendIcon,
  PlusIcon,
  HousePlus,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const generateSessionId = () => nanoid();

interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export function ChatUI() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [isProcessing, setIsProcessing] = useState(false); // Add this line

  const addMessage = useCallback((message: string, isUser = false) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { text: message, isUser, timestamp: new Date() },
    ]);
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim()) return;

    setIsProcessing(true);
    addMessage(input, true);
    setInput("");

    try {
      const response = await fetch("http://localhost:8000/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          questions: input,
          session: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      setIsProcessing(false);
      addMessage(data.message);
    } catch (error) {
      console.error("Error:", error);
      setIsProcessing(false);
      addMessage("Sorry, there was an error processing your request.");
    }
  }, [input, sessionId, addMessage]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(generateSessionId());
  }, []);

  useEffect(() => {
    setSessionId(generateSessionId());
  }, []);
  return (
    <div className="flex h-full flex-col">
      <header className="sticky top-0 z-10 border-b bg-background px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Avatar className="h-8 w-8">
              <AvatarImage src="/placeholder-user.jpg" alt="Bot Avatar" />
              <AvatarFallback>B</AvatarFallback>
            </Avatar>
            <div>
              <h3 className="text-lg font-medium">Chat With Documents</h3>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={clearChat}>
              <HousePlus className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </header>
      <div className="flex-1 overflow-auto p-6">
        <div className="grid gap-6">
          {messages.map((message, index) => (
            <div key={index} className="flex items-start gap-4">
              <Avatar className="h-10 w-10 shrink-0">
                <AvatarImage
                  src="/placeholder-user.jpg"
                  alt={message.isUser ? "User Avatar" : "Bot Avatar"}
                />
                <AvatarFallback>{message.isUser ? "U" : "B"}</AvatarFallback>
              </Avatar>
              <div className="grid gap-2">
                <div
                  className={`rounded-lg ${
                    message.isUser
                      ? "bg-muted"
                      : "bg-primary text-primary-foreground"
                  } p-4 text-sm`}
                >
                  <p>{message.text}</p>
                </div>
                <div className="text-xs text-muted-foreground">
                  <time dateTime={message.timestamp.toISOString()}>
                    {message.timestamp.toLocaleTimeString()}
                  </time>
                </div>
              </div>
            </div>
          ))}
          {isProcessing && (
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 animate-pulse rounded-full bg-primary"></div>
              <div className="h-2 w-2 animate-pulse rounded-full bg-primary"></div>
              <div className="h-2 w-2 animate-pulse rounded-full bg-primary"></div>
              <span className="text-sm text-muted-foreground">
                Bot is typing...
              </span>
            </div>
          )}
        </div>
      </div>
      <div className="border-t bg-background px-6 py-4">
        <div className="relative">
          <Textarea
            placeholder="Type your message..."
            className="h-10 w-full resize-none rounded-lg border border-input bg-transparent pr-16 focus:outline-none focus:ring-1 focus:ring-ring"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
          />
          <Button
            type="submit"
            variant="ghost"
            size="icon"
            className="absolute right-2 top-2"
            onClick={sendMessage}
          >
            <SendIcon className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
