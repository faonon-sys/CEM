import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import NetworkGraph from './components/NetworkGraph/NetworkGraph'
import Dashboard from './components/Dashboard/Dashboard'
import ComparisonView from './components/Comparison/ComparisonView'
import CalibrationInterface from './components/Calibration/CalibrationInterface'
import TrajectoryView from './components/Trajectory/TrajectoryView'
import SurfaceAnalysis from './components/SurfaceAnalysis/SurfaceAnalysis'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="nav">
          <div className="nav-brand">
            <h1>Structured Reasoning System</h1>
            <p>Sprint 2-6: Complete Platform</p>
          </div>
          <div className="nav-links">
            <Link to="/">Network Graph</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/surface-analysis/123e4567-e89b-12d3-a456-426614174000">Surface Analysis</Link>
            <Link to="/comparison">Comparison</Link>
            <Link to="/calibration">Calibration</Link>
            <Link to="/trajectory">Trajectories</Link>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<NetworkGraph />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/surface-analysis/:scenarioId" element={<SurfaceAnalysis />} />
            <Route path="/comparison" element={<ComparisonView />} />
            <Route path="/calibration" element={<CalibrationInterface />} />
            <Route path="/trajectory" element={<TrajectoryView />} />
            <Route path="/trajectory/:trajectoryId" element={<TrajectoryView />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
