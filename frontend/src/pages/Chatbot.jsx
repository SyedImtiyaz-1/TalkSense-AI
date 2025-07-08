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
    <div className="container mx-auto py-8">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>AI Chatbot</CardTitle>
          <CardDescription>Chat with our AI assistant about call-related insights and questions.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="h-[500px] overflow-y-auto space-y-4 p-4 rounded-lg border bg-muted/50">
            {messages.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "flex gap-3 p-4 rounded-lg",
                  message.role === 'user' 
                    ? "ml-auto max-w-[80%] bg-primary text-primary-foreground" 
                    : "mr-auto max-w-[80%] bg-secondary text-secondary-foreground"
                )}
              >
                <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-background text-foreground">
                  {message.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>
                <div className="flex-1">
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="min-h-[50px] flex-1 bg-muted/50"
            />
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
            >
              <Send className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 