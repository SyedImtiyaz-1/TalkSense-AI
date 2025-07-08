import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

const CallSimulator = () => {
  const [isCallActive, setIsCallActive] = useState(false);
  const [callDuration, setCallDuration] = useState(0);
  const [transcript, setTranscript] = useState('');
  const [insights, setInsights] = useState([]);
  const [sentiment, setSentiment] = useState('neutral');
  const [selectedScenario, setSelectedScenario] = useState('customer_support');

  const scenarios = [
    { id: 'customer_support', name: 'Customer Support Issue' },
    { id: 'sales_inquiry', name: 'Sales Inquiry' },
    { id: 'technical_issue', name: 'Technical Issue' },
    { id: 'billing_question', name: 'Billing Question' },
  ];

  useEffect(() => {
    let timer;
    if (isCallActive) {
      timer = setInterval(() => {
        setCallDuration(prev => prev + 1);
        simulateCallProgress(callDuration + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isCallActive, callDuration]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const simulateCallProgress = (seconds) => {
    // Simulate a customer support call
    if (seconds === 3) {
      setTranscript('Customer: Hi, I need help with my account.');
      setInsights([{ type: 'intent', text: 'Account assistance request detected' }]);
      setSentiment('neutral');
    } else if (seconds === 6) {
      setTranscript(prev => prev + '\nAgent: Hello! I\'d be happy to help you with your account. Could you please verify your account number?');
      setInsights(prev => [...prev, { type: 'entity', text: 'Account verification initiated' }]);
    } else if (seconds === 9) {
      setTranscript(prev => prev + '\nCustomer: Yes, it\'s 12345. I\'m having trouble logging in.');
      setInsights(prev => [...prev, { type: 'intent', text: 'Login issue identified' }]);
      setSentiment('negative');
    } else if (seconds === 12) {
      setTranscript(prev => prev + '\nAgent: I understand your frustration. Let me help you reset your password.');
      setInsights(prev => [...prev, { type: 'sentiment', text: 'Agent showing empathy' }]);
    } else if (seconds === 15) {
      setTranscript(prev => prev + '\nCustomer: Thank you, that would be helpful.');
      setSentiment('positive');
      setInsights(prev => [...prev, { type: 'resolution', text: 'Customer accepting proposed solution' }]);
    } else if (seconds === 18) {
      setTranscript(prev => prev + '\nAgent: I\'ve sent a password reset link to your email. Is there anything else I can help you with?');
      setInsights(prev => [
        ...prev,
        { type: 'action', text: 'Password reset link sent' },
        { type: 'summary', text: 'Successfully resolved login issue' }
      ]);
    }
  };

  const startCall = () => {
    setIsCallActive(true);
    setCallDuration(0);
    setTranscript('');
    setInsights([]);
    setSentiment('neutral');
  };

  const endCall = () => {
    setIsCallActive(false);
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'intent':
        return 'text-blue-500 dark:text-blue-400';
      case 'entity':
        return 'text-purple-500 dark:text-purple-400';
      case 'sentiment':
        return 'text-green-500 dark:text-green-400';
      case 'resolution':
        return 'text-yellow-500 dark:text-yellow-400';
      case 'summary':
        return 'text-orange-500 dark:text-orange-400';
      case 'action':
        return 'text-pink-500 dark:text-pink-400';
      default:
        return 'text-gray-500 dark:text-gray-400';
    }
  };

  const getSentimentColor = () => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-500 dark:text-green-400';
      case 'negative':
        return 'text-red-500 dark:text-red-400';
      default:
        return 'text-gray-500 dark:text-gray-400';
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight">Call Simulator</h1>
          <p className="text-muted-foreground">
            Practice customer interactions and analyze call performance in real-time.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-[2fr,1fr]">
          <div className="flex flex-col gap-6">
            <Card className="border shadow-sm dark:border-gray-800">
              <CardHeader>
                <CardTitle>Simulation Controls</CardTitle>
                <CardDescription>Select a scenario and manage your call</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-wrap items-center gap-4">
                  <select
                    value={selectedScenario}
                    onChange={(e) => setSelectedScenario(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 sm:w-[200px]"
                  >
                    {scenarios.map(scenario => (
                      <option key={scenario.id} value={scenario.id}>
                        {scenario.name}
                      </option>
                    ))}
                  </select>
                  <Button
                    onClick={isCallActive ? endCall : startCall}
                    variant={isCallActive ? "destructive" : "default"}
                    className="dark:bg-blue-600 dark:hover:bg-blue-700 dark:text-white"
                  >
                    {isCallActive ? "End Call" : "Start Call"}
                  </Button>
                  {isCallActive && (
                    <span className="text-sm text-muted-foreground dark:text-gray-400">
                      Duration: {formatTime(callDuration)}
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border shadow-sm dark:border-gray-800">
              <CardHeader>
                <CardTitle>Live Transcription</CardTitle>
                <CardDescription>Real-time conversation transcript</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="min-h-[400px] p-4 rounded-md bg-muted whitespace-pre-line dark:bg-gray-800 dark:text-gray-100 border dark:border-gray-700 overflow-y-auto">
                  {transcript || "Transcription will appear here..."}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="flex flex-col gap-6">
            <Card className="border shadow-sm dark:border-gray-800">
              <CardHeader>
                <CardTitle>Real-time Insights</CardTitle>
                <CardDescription>AI-powered call analysis</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {insights.map((insight, index) => (
                    <div key={index} className="flex items-start gap-2 p-3 rounded-md bg-muted/50 dark:bg-gray-800/50">
                      <span className={`font-medium ${getInsightColor(insight.type)}`}>
                        {insight.type.charAt(0).toUpperCase() + insight.type.slice(1)}:
                      </span>
                      <span className="dark:text-gray-300">{insight.text}</span>
                    </div>
                  ))}
                  {insights.length === 0 && (
                    <p className="text-sm text-muted-foreground text-center dark:text-gray-400">
                      Insights will appear during the call
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="border shadow-sm dark:border-gray-800">
              <CardHeader>
                <CardTitle>Call Analytics</CardTitle>
                <CardDescription>Performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="p-4 rounded-md bg-muted/50 dark:bg-gray-800/50">
                    <span className="text-sm font-medium dark:text-gray-300">Sentiment:</span>
                    <span className={`ml-2 capitalize ${getSentimentColor()}`}>
                      {sentiment}
                    </span>
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium dark:text-gray-300">Customer Satisfaction</span>
                        <span className="text-sm text-muted-foreground dark:text-gray-400">
                          {sentiment === 'positive' ? '80%' : sentiment === 'neutral' ? '50%' : '30%'}
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-muted dark:bg-gray-700">
                        <div
                          className="h-full rounded-full bg-green-500 dark:bg-green-600 transition-all duration-500"
                          style={{ width: `${sentiment === 'positive' ? 80 : sentiment === 'neutral' ? 50 : 30}%` }}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm font-medium dark:text-gray-300">Agent Performance</span>
                        <span className="text-sm text-muted-foreground dark:text-gray-400">75%</span>
                      </div>
                      <div className="h-2 rounded-full bg-muted dark:bg-gray-700">
                        <div
                          className="h-full rounded-full bg-blue-500 dark:bg-blue-600 transition-all duration-500"
                          style={{ width: '75%' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallSimulator; 