import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './components/Dashboard';
import ProjectDetail from './components/ProjectDetail';
import EscalationQueue from './components/EscalationQueue';
import AuditLog from './components/AuditLog';
import TeamPanel from './components/TeamPanel';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/escalations" element={<EscalationQueue />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/team" element={<TeamPanel />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
