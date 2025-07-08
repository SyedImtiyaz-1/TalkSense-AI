import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Link } from "react-router-dom";

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Welcome to Call Insights</h1>
        <p className="text-muted-foreground">
          Enhance your call center operations with AI-powered insights and tools.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>AI Chatbot</CardTitle>
            <CardDescription>
              Interact with our AI assistant for instant support and insights.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link to="/chatbot">Start Chat</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Voice Transcriber</CardTitle>
            <CardDescription>
              Convert voice recordings to text with advanced transcription.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link to="/voice-transcriber">Start Transcribing</Link>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Call Simulator</CardTitle>
            <CardDescription>
              Practice and analyze simulated customer interactions.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link to="/call-simulator">Start Simulation</Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-4">
        <h2 className="text-2xl font-bold tracking-tight">Recent Activities</h2>
        <div className="grid gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Latest Interactions</CardTitle>
              <CardDescription>Your recent interactions and transcriptions</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                <li className="text-sm">AI Chat Session - 2 mins ago</li>
                <li className="text-sm">Voice Transcription - 15 mins ago</li>
                <li className="text-sm">Call Simulation - 1 hour ago</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 