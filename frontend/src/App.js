import React, { useState } from 'react';
import './App.css';

function App() {
  const [jobDescription, setJobDescription] = useState('');
  const [matchedProjects, setMatchedProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [bullets, setBullets] = useState([]);
  const [loading, setLoading] = useState(false);
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';


  const searchProjects = async () => {
    setLoading(true);
    setBullets([]);
    setSelectedProject(null);
    
    try {
      const response = await fetch(`${API_URL}/api/search-projects`
, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: jobDescription,
          limit: 3
        })
      });
      const data = await response.json();
      setMatchedProjects(data.results || []);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to search projects');
    }
    setLoading(false);
  };

  const generateBullets = async (projectId) => {
    setLoading(true);
    setSelectedProject(projectId);
    
    try {
      const response = await fetch(`${API_URL}/api/generate`
, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_description: jobDescription,
          project_id: projectId,
          num_bullets: 3
        })
      });
      const data = await response.json();
      setBullets(data.bullets || []);
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate bullets');
    }
    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Resume Tailor</h1>
        <p>AI-powered resume customization</p>
      </header>

      <div className="container">
        <div className="input-section">
          <h2>Job Description</h2>
          <textarea
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            rows={10}
          />
          <button onClick={searchProjects} disabled={loading || !jobDescription}>
            {loading ? 'Searching...' : 'Find Relevant Experience'}
          </button>
        </div>

        {matchedProjects.length > 0 && (
          <div className="projects-section">
            <h2>Top 3 Matching Projects</h2>
            <p>Select a project to generate tailored bullets:</p>
            {matchedProjects.map((project) => (
              <div key={project.id} className="project-card">
                <h3>{project.title}</h3>
                <p><strong>Type:</strong> {project.type}</p>
                <p><strong>Date:</strong> {project.date_range || 'N/A'}</p>
                <p><strong>Relevance:</strong> {(project.similarity * 100).toFixed(0)}%</p>
                <button 
                  onClick={() => generateBullets(project.id)}
                  disabled={loading}
                >
                  {loading && selectedProject === project.id ? 'Generating...' : 'Generate Bullets'}
                </button>
              </div>
            ))}
          </div>
        )}

        {bullets.length > 0 && (
          <div className="results-section">
            <h2>Generated Bullets</h2>
            <ul>
              {bullets.map((bullet, i) => (
                <li key={i}>{bullet}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;