import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import Chatbot from './pages/Chatbot';
import VoiceTranscriber from './pages/VoiceTranscriber';
import CallSimulator from './pages/CallSimulator';
import DataManager from './pages/DataManager';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chatbot" element={<Chatbot />} />
          <Route path="/voice-transcriber" element={<VoiceTranscriber />} />
          <Route path="/call-simulator" element={<CallSimulator />} />
          <Route path="/data-manager" element={<DataManager />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
