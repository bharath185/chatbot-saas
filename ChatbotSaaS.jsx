import React, { useState, useEffect } from 'react';
import { Settings, Plus, Trash2, Code, BarChart3, LogOut, Menu, X } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export default function ChatbotSaaS() {
  const [page, setPage] = useState('login'); // login, register, dashboard, chatbot-details
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [businessName, setBusinessName] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [chatbots, setChatbots] = useState([]);
  const [selectedChatbot, setSelectedChatbot] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [newChatbotName, setNewChatbotName] = useState('');
  const [newChatbotDesc, setNewChatbotDesc] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('You are a helpful customer service assistant.');
  const [widgetColor, setWidgetColor] = useState('#007bff');
  const [welcomeMessage, setWelcomeMessage] = useState('Hello! How can I help you today?');
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (token) {
      setPage('dashboard');
      fetchChatbots();
      fetchUsage();
    }
  }, [token]);

  const fetchChatbots = async () => {
    try {
      const response = await fetch(`${API_URL}/chatbots`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setChatbots(data);
    } catch (err) {
      console.error('Error fetching chatbots:', err);
    }
  };

  const fetchUsage = async () => {
    try {
      const response = await fetch(`${API_URL}/usage`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setUsage(data);
    } catch (err) {
      console.error('Error fetching usage:', err);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, business_name: businessName })
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
      } else {
        alert(data.error);
      }
    } catch (err) {
      alert('Registration failed: ' + err.message);
    }
    setLoading(false);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
      } else {
        alert(data.error);
      }
    } catch (err) {
      alert('Login failed: ' + err.message);
    }
    setLoading(false);
  };

  const handleCreateChatbot = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/chatbots`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newChatbotName,
          description: newChatbotDesc,
          system_prompt: systemPrompt,
          widget_color: widgetColor,
          welcome_message: welcomeMessage
        })
      });
      const data = await response.json();
      if (response.ok) {
        fetchChatbots();
        setShowForm(false);
        setNewChatbotName('');
        setNewChatbotDesc('');
      } else {
        alert(data.error);
      }
    } catch (err) {
      alert('Error creating chatbot: ' + err.message);
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setPage('login');
    setChatbots([]);
  };

  const handleSelectChatbot = async (chatbotId) => {
    try {
      const response = await fetch(`${API_URL}/chatbots/${chatbotId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setSelectedChatbot(data);
      setPage('chatbot-details');
    } catch (err) {
      alert('Error loading chatbot: ' + err.message);
    }
  };

  if (page === 'login') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
          <h1 className="text-3xl font-bold text-center mb-2">ChatBot SaaS</h1>
          <p className="text-center text-gray-600 mb-8">Customer Service Made Easy</p>
          
          <form onSubmit={handleLogin} className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
          
          <p className="text-center text-gray-600 mt-4">
            Don't have an account?{' '}
            <button
              onClick={() => setPage('register')}
              className="text-blue-600 font-semibold hover:underline"
            >
              Register
            </button>
          </p>
        </div>
      </div>
    );
  }

  if (page === 'register') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
          <h1 className="text-3xl font-bold text-center mb-8">Create Account</h1>
          
          <form onSubmit={handleRegister} className="space-y-4">
            <input
              type="text"
              placeholder="Business Name"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Account'}
            </button>
          </form>
          
          <p className="text-center text-gray-600 mt-4">
            Already have an account?{' '}
            <button
              onClick={() => setPage('login')}
              className="text-blue-600 font-semibold hover:underline"
            >
              Login
            </button>
          </p>
        </div>
      </div>
    );
  }

  if (page === 'dashboard') {
    return (
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow-md sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-blue-600">ChatBot SaaS</h1>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden"
            >
              {mobileMenuOpen ? <X /> : <Menu />}
            </button>
            <button
              onClick={handleLogout}
              className="hidden md:flex items-center gap-2 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
            >
              <LogOut size={18} /> Logout
            </button>
          </div>
          {mobileMenuOpen && (
            <div className="md:hidden bg-gray-50 border-t p-4">
              <button
                onClick={handleLogout}
                className="w-full text-left flex items-center gap-2 text-red-500 font-semibold"
              >
                <LogOut size={18} /> Logout
              </button>
            </div>
          )}
        </nav>

        <div className="max-w-7xl mx-auto p-4 md:p-8">
          {/* Usage Stats */}
          {usage && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm">Total Chatbots</p>
                <p className="text-3xl font-bold text-blue-600">{chatbots.length}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm">Tokens Used</p>
                <p className="text-3xl font-bold text-green-600">{usage.total_tokens_used.toLocaleString()}</p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm">Est. Monthly Cost</p>
                <p className="text-3xl font-bold text-purple-600">₹{(usage.estimated_monthly_cost * 80).toFixed(0)}</p>
              </div>
            </div>
          )}

          {/* Create Chatbot Form */}
          {showForm && (
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <h2 className="text-xl font-bold mb-4">Create New Chatbot</h2>
              <form onSubmit={handleCreateChatbot} className="space-y-4">
                <input
                  type="text"
                  placeholder="Chatbot Name"
                  value={newChatbotName}
                  onChange={(e) => setNewChatbotName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  required
                />
                <input
                  type="text"
                  placeholder="Description"
                  value={newChatbotDesc}
                  onChange={(e) => setNewChatbotDesc(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
                <textarea
                  placeholder="System Prompt"
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg h-24"
                />
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-semibold mb-2">Widget Color</label>
                    <input
                      type="color"
                      value={widgetColor}
                      onChange={(e) => setWidgetColor(e.target.value)}
                      className="w-full h-10 border border-gray-300 rounded-lg"
                    />
                  </div>
                </div>
                <input
                  type="text"
                  placeholder="Welcome Message"
                  value={welcomeMessage}
                  onChange={(e) => setWelcomeMessage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                  >
                    {loading ? 'Creating...' : 'Create Chatbot'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="flex-1 bg-gray-400 text-white py-2 rounded-lg font-semibold hover:bg-gray-500"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 flex items-center gap-2 mb-8"
            >
              <Plus size={20} /> Create New Chatbot
            </button>
          )}

          {/* Chatbots List */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {chatbots.map((chatbot) => (
              <div key={chatbot.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                <h3 className="text-lg font-bold mb-2">{chatbot.name}</h3>
                <p className="text-gray-600 text-sm mb-4">{chatbot.description || 'No description'}</p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleSelectChatbot(chatbot.id)}
                    className="flex-1 bg-blue-500 text-white py-2 rounded-lg text-sm font-semibold hover:bg-blue-600 flex items-center justify-center gap-2"
                  >
                    <Settings size={16} /> Manage
                  </button>
                  <button
                    onClick={() => {
                      // Copy embed code logic
                      alert('Embed code feature coming soon!');
                    }}
                    className="flex-1 bg-green-500 text-white py-2 rounded-lg text-sm font-semibold hover:bg-green-600 flex items-center justify-center gap-2"
                  >
                    <Code size={16} /> Embed
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (page === 'chatbot-details' && selectedChatbot) {
    return (
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-md">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <button
              onClick={() => setPage('dashboard')}
              className="text-blue-600 font-semibold hover:underline"
            >
              ← Back to Dashboard
            </button>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </nav>

        <div className="max-w-4xl mx-auto p-4 md:p-8">
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h1 className="text-3xl font-bold mb-4">{selectedChatbot.name}</h1>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold mb-2">System Prompt</label>
                <p className="bg-gray-50 p-4 rounded-lg">{selectedChatbot.system_prompt}</p>
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Widget Color</label>
                <div
                  className="w-20 h-20 rounded-lg border-2 border-gray-300"
                  style={{ backgroundColor: selectedChatbot.widget_color }}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold mb-2">Welcome Message</label>
                <p className="bg-gray-50 p-4 rounded-lg">{selectedChatbot.welcome_message}</p>
              </div>
            </div>

            <div className="mt-6">
              <h2 className="text-lg font-bold mb-4">Embed Code</h2>
              <button
                onClick={() => alert('Embed code functionality coming soon!')}
                className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 flex items-center gap-2"
              >
                <Code size={18} /> Get Embed Code
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
