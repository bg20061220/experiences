import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ExperienceManager } from './components/ExperienceManager';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ServerStatusContext = createContext({ serverReady: true });
const useServerStatus = () => useContext(ServerStatusContext);

function ServerWarmup({ children }) {
  const [serverReady, setServerReady] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => {
        if (res.ok) setServerReady(true);
      })
      .catch(() => {
        // Retry after a delay if the first attempt fails
        const retry = setInterval(() => {
          fetch(`${API_URL}/health`)
            .then((res) => {
              if (res.ok) {
                setServerReady(true);
                clearInterval(retry);
              }
            })
            .catch(() => {});
        }, 3000);
        return () => clearInterval(retry);
      });
  }, []);

  return (
    <ServerStatusContext.Provider value={{ serverReady }}>
      {children}
    </ServerStatusContext.Provider>
  );
}

function MainApp() {
  const [activeTab, setActiveTab] = useState('generate');
  const [jobDescription, setJobDescription] = useState('');
  const [matchedExperiences, setMatchedExperiences] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [projects, setProjects] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState(null);

  const { user, signOut, getAccessToken } = useAuth();

  // Helper to make authenticated API calls
  const authFetch = async (url, options = {}) => {
    const token = getAccessToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      await signOut();
      throw new Error('Session expired. Please sign in again.');
    }

    return response;
  };

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const searchExperiences = async () => {
    setSearchLoading(true);
    setProjects([]);
    setSelectedIds(new Set());

    try {
      const response = await authFetch(`${API_URL}/api/search`, {
        method: 'POST',
        body: JSON.stringify({
          query: jobDescription,
          limit: 10
        })
      });
      const data = await response.json();
      const results = data.results || [];
      setMatchedExperiences(results);

      // Auto-select all top matches
      setSelectedIds(new Set(results.map(exp => exp.id)));

      if (data.message) {
        alert(data.message);
      }
    } catch (error) {
      console.error('Error:', error);
      alert(error.message || 'Failed to search experiences');
    }
    setSearchLoading(false);
  };

  const toggleSelection = (id) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const selectAll = () => {
    setSelectedIds(new Set(matchedExperiences.map(exp => exp.id)));
  };

  const selectNone = () => {
    setSelectedIds(new Set());
  };

  const generateBullets = async () => {
    if (selectedIds.size === 0) {
      alert('Please select at least one experience');
      return;
    }

    setGenerateLoading(true);

    try {
      const response = await authFetch(`${API_URL}/api/generate`, {
        method: 'POST',
        body: JSON.stringify({
          job_description: jobDescription,
          experience_ids: Array.from(selectedIds)
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to generate bullets');
      }

      const data = await response.json();
      setProjects(data.projects || []);
    } catch (error) {
      console.error('Error:', error);
      alert(error.message || 'Failed to generate bullets');
    }
    setGenerateLoading(false);
  };

  const copyBullet = async (bullet, index) => {
    try {
      await navigator.clipboard.writeText(bullet);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const copyAllBullets = async () => {
    try {
      const text = projects.map(p =>
        `${p.project}\n${p.bullets.map(b => `• ${b}`).join('\n')}`
      ).join('\n\n');
      await navigator.clipboard.writeText(text);
      setCopiedIndex('all');
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Resume Tailor</h1>
        <p>Add your work experience, projects, and volunteering in Manage Experiences and then paste a job description to get your top 3 most relevant matches with ATS-friendly bullets.</p>
        <div className="user-info">
          <span>{user?.email}</span>
          <button onClick={handleSignOut} className="sign-out-btn">
            Sign Out
          </button>
        </div>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'generate' ? 'active' : ''}`}
          onClick={() => setActiveTab('generate')}
        >
          Generate Bullets
        </button>
        <button
          className={`tab ${activeTab === 'manage' ? 'active' : ''}`}
          onClick={() => setActiveTab('manage')}
        >
          Manage Experiences
        </button>
      </div>

      <div className="container">
        {activeTab === 'generate' ? (
          <>
            <div className="input-section">
              <h2>Step 1: Paste Qualifications</h2>
              <textarea
                placeholder="Paste the job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={8}
              />
              <button
                onClick={searchExperiences}
                disabled={searchLoading || !jobDescription.trim()}
              >
                {searchLoading ? 'Finding Matches...' : 'Find Matching Experiences'}
              </button>
            </div>

            {matchedExperiences.length > 0 && (
              <div className="matches-section">
                <div className="matches-header">
                  <h2>Step 2: Select Experiences</h2>
                  <div className="selection-actions">
                    <button onClick={selectAll} className="link-btn">Select All</button>
                    <span className="separator">|</span>
                    <button onClick={selectNone} className="link-btn">Select None</button>
                  </div>
                </div>
                <p className="matches-hint">
                  {selectedIds.size} of {matchedExperiences.length} selected.
                </p>

                <div className="matches-list">
                  {matchedExperiences.map((exp) => {
                    const isSelected = selectedIds.has(exp.id);

                    return (
                      <label
                        key={exp.id}
                        className={`match-card ${isSelected ? 'selected' : ''}`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleSelection(exp.id)}
                        />
                        <div className="match-content">
                          <div className="match-header">
                            <h3>{exp.title}</h3>
                          </div>
                          <p className="match-meta">
                            {exp.type} {exp.date_range && `• ${exp.date_range}`}
                          </p>
                          {exp.skills && exp.skills.length > 0 && (
                            <div className="match-skills">
                              {exp.skills.slice(0, 5).map((skill) => (
                                <span key={skill} className="skill-tag-sm">{skill}</span>
                              ))}
                              {exp.skills.length > 5 && (
                                <span className="skill-tag-sm more">+{exp.skills.length - 5}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </label>
                    );
                  })}
                </div>

                <button
                  onClick={generateBullets}
                  disabled={generateLoading || selectedIds.size === 0}
                  className="generate-btn"
                >
                  {generateLoading
                    ? 'Generating...'
                    : `Generate Bullets from ${selectedIds.size} Experience${selectedIds.size !== 1 ? 's' : ''}`
                  }
                </button>
              </div>
            )}

            {projects.length > 0 && (
              <div className="results-section">
                <div className="results-header">
                  <h2>Step 3: Your Tailored Bullets</h2>
                  <button onClick={copyAllBullets} className="copy-all-btn">
                    {copiedIndex === 'all' ? 'Copied!' : 'Copy All'}
                  </button>
                </div>
                {projects.map((project, pIndex) => (
                  <div key={pIndex} className="project-bullets">
                    <h3 className="project-title">{project.project}</h3>
                    <ul className="bullets-list">
                      {project.bullets.map((bullet, bIndex) => {
                        const key = `${pIndex}-${bIndex}`;
                        return (
                          <li key={key} className="bullet-item">
                            <span className="bullet-text">{bullet}</span>
                            <button
                              onClick={() => copyBullet(bullet, key)}
                              className="copy-btn"
                              title="Copy to clipboard"
                            >
                              {copiedIndex === key ? 'Copied!' : 'Copy'}
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          <ExperienceManager authFetch={authFetch} apiUrl={API_URL} />
        )}
      </div>
    </div>
  );
}

function ServerGate({ children }) {
  const { serverReady } = useServerStatus();

  if (!serverReady) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Our server is waking up, this will take 15-20 seconds...</p>
      </div>
    );
  }

  return children;
}

function App() {
  return (
    <ServerWarmup>
      <AuthProvider>
        <ProtectedRoute>
          <ServerGate>
            <MainApp />
          </ServerGate>
        </ProtectedRoute>
      </AuthProvider>
    </ServerWarmup>
  );
}

export default App;