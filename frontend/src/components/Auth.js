import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const { signIn, signUp } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);

    try {
      if (isLogin) {
        await signIn(email, password);
      } else {
        await signUp(email, password);
        setMessage('Check your email for a confirmation link!');
      }
    } catch (err) {
      const msg = err.message || '';
      const secondsMatch = msg.match(/(\d+)\s*second/i);
      if (secondsMatch) {
        setError(`We're on a free plan with limited auth requests. Please wait ${secondsMatch[1]} seconds before trying again.`);
      } else {
        setError(msg);
      }
    }

    setLoading(false);
  };

  return (
    <div className="hero-container">
      <div className="hero-top">
        <div className="hero-left">
          <div className="hero-badge">AI-Powered Resume Tool</div>
          <h1 className="hero-title">
            Tailor your resume to <span className="hero-highlight">any job</span> in seconds
          </h1>
        </div>

        <div className="hero-right">
          <div className="hero-feature-card">
            <h3>Import from LinkedIn</h3>
            <p>Paste your LinkedIn experience, projects, and volunteering sections. Our AI parses them into structured entries automatically with no manual typing needed.</p>
          </div>
          <div className="hero-feature-card">
            <h3>AI-Matched Experiences</h3>
            <p>Paste any job description and our AI finds your most relevant experiences using semantic search, ranking them by how well they match the role.</p>
          </div>
          <div className="hero-feature-card">
            <h3>ATS-Friendly Bullet Generation</h3>
            <p>Generate tailored, ATS-optimized resume bullet points with strong action verbs, relevant keywords, and quantified results — ready to pass applicant tracking systems and impress recruiters.</p>
          </div>
        </div>
      </div>

      <div className="hero-bottom">
        <div className="auth-box">
          <h2>{isLogin ? 'Sign In' : 'Create Account'}</h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Your password"
                minLength={6}
                required
              />
            </div>

            {error && <div className="error-message">{error}</div>}
            {message && <div className="success-message">{message}</div>}

            <button type="submit" disabled={loading}>
              {loading ? 'Loading...' : isLogin ? 'Sign In' : 'Sign Up'}
            </button>
          </form>

          <p className="auth-toggle">
            {isLogin ? "Don't have an account? " : 'Already have an account? '}
            <button
              type="button"
              className="link-button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
                setMessage('');
              }}
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
