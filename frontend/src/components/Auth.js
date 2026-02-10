import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const { signIn, signUp, signInWithGoogle } = useAuth();

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

          <button
            type="button"
            className="google-btn"
            onClick={async () => {
              try {
                await signInWithGoogle();
              } catch (err) {
                setError(err.message);
              }
            }}
          >
            <svg width="18" height="18" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            Continue with Google
          </button>

          <div className="auth-divider">
            <span>or</span>
          </div>

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
