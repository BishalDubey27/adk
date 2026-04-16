import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { api } from '../api/client';

const ProjectDetail = () => {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProject();
  }, [id]);

  const loadProject = async () => {
    try {
      const data = await api.projects.get(id);
      setProject(data.project);
      setTasks(data.tasks || []);
    } catch (error) {
      console.error('Failed to load project:', error);
    } finally {
      setLoading(false);
    }
  };

  const tasksByStatus = {
    todo: tasks.filter(t => t.status === 'todo'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    blocked: tasks.filter(t => t.status === 'blocked'),
    done: tasks.filter(t => t.status === 'done'),
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!project) return <div className="p-8">Project not found</div>;

  return (
    <div className="p-8">
      <Link to="/" className="flex items-center gap-2 text-text-secondary hover:text-text-primary mb-6">
        <ChevronLeft size={20} />
        <span className="text-sm">Back to Dashboard</span>
      </Link>

      <div className="mb-8">
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-lg font-semibold text-text-primary">{project.name}</h1>
          <span className={`text-xs px-2 py-1 rounded-full ${
            project.priority === 'critical' ? 'bg-danger/20 text-danger' :
            project.priority === 'high' ? 'bg-warning/20 text-warning' :
            'bg-primary/20 text-primary'
          }`}>
            {project.priority}
          </span>
          <span className="text-xs px-2 py-1 rounded-full bg-surface-raised text-text-secondary">
            {project.status}
          </span>
        </div>
        <p className="text-sm text-text-secondary">{project.description}</p>
        <div className="flex items-center gap-6 mt-4 text-sm text-text-secondary">
          <span>Deadline: {project.deadline}</span>
          <span>Confidence: <span className={
            project.confidence_score > 0.85 ? 'text-success' :
            project.confidence_score > 0.65 ? 'text-warning' : 'text-danger'
          }>{project.confidence_score?.toFixed(2)}</span></span>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {Object.entries(tasksByStatus).map(([status, statusTasks]) => (
          <div key={status} className="bg-surface rounded-md p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-text-primary capitalize">
                {status.replace('_', ' ')}
              </h3>
              <span className="text-xs px-2 py-1 bg-surface-raised rounded-full text-text-secondary">
                {statusTasks.length}
              </span>
            </div>
            <div className="space-y-3">
              {statusTasks.map((task) => (
                <div key={task.id} className="bg-bg p-3 rounded-md border border-border">
                  <h4 className="text-sm font-medium text-text-primary mb-2">{task.title}</h4>
                  {task.assigned_to_name && (
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center text-white text-xs">
                        {task.assigned_to_name.charAt(0)}
                      </div>
                      <span className="text-xs text-text-secondary">{task.assigned_to_name}</span>
                    </div>
                  )}
                  <div className="text-xs text-text-secondary">
                    {task.estimated_hours}h estimated
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectDetail;
