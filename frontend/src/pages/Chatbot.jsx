import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Bot, Send, User } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Chatbot() {
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState('');
  const [isLoading, setIsLoading] = React.useState(false);
  const messagesEndRef = React.useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      const botMessage = { role: 'assistant', content: 'This is a simulated response. The actual API integration will be implemented later.' };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-0 px-0 sm:py-8 sm:px-0 flex flex-col items-center min-h-[100dvh] bg-gradient-to-b via-white ">
      <Card className="max-w-2xl w-full flex flex-col h-[90dvh] sm:h-[80dvh] shadow-2xl border-0 sm:rounded-2xl rounded-none overflow-hidden bg-white">
        <CardHeader className="bg-white border-b border-border px-4 py-3">
          <CardTitle className="text-xl sm:text-2xl font-bold">AI Chatbot</CardTitle>
          <CardDescription className="text-base sm:text-lg">Chat with our AI assistant about call-related insights and questions.</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col justify-end p-0">
          <div className="flex-1 overflow-y-auto px-2 sm:px-6 py-4 bg-gradient-to-b from-white/80 to-blue-50 space-y-3" style={{scrollbarWidth: 'thin'}}>
            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "flex items-end gap-2 sm:gap-3 group",
                  message.role === 'user' 
                    ? "justify-end" 
                    : "justify-start"
                )}
              >
                {message.role === 'assistant' && (
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-blue-100 text-blue-600 shadow-md border border-blue-200">
                    <Bot className="h-5 w-5" />
                  </div>
                )}
                <div
                  className={cn(
                    "px-4 py-2 rounded-2xl shadow-md max-w-[85vw] sm:max-w-[70%] text-base transition-all duration-300 animate-fadeIn",
                    message.role === 'user'
                      ? "bg-blue-600 text-white rounded-br-md"
                      : "bg-white text-blue-900 border border-blue-100 rounded-bl-md"
                  )}
                >
                  {message.content}
                </div>
                {message.role === 'user' && (
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-blue-600 text-white shadow-md border border-blue-300">
                    <User className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          {/* Sticky input bar */}
          <form onSubmit={handleSubmit} className="sticky bottom-0 left-0 w-full bg-white/90 backdrop-blur border-t border-border flex gap-2 px-2 sm:px-6 py-3 z-10">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="min-h-[44px] flex-1 bg-muted/50 text-base resize-none rounded-xl border border-blue-200 focus:border-blue-400 focus:ring-blue-200 shadow-sm"
            />
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white hover:bg-blue-700 w-14 h-12 rounded-xl flex items-center justify-center text-base shadow-lg"
            >
              <Send className="h-6 w-6" />
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 