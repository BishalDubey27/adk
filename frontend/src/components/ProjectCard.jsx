import { useNavigate } from 'react-router-dom';
import { Calendar, Gauge } from 'lucide-react';

const ProjectCard = ({ project }) => {
  const navigate = useNavigate();
  
  const getConfidenceColor = (score) => {
    if (score > 0.85) return 'border-success';
    if (score > 0.65) return 'border-warning';
    return 'border-danger';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'bg-danger/20 text-danger',
      high: 'bg-warning/20 text-warning',
      medium: 'bg-primary/20 text-primary',
      low: 'bg-text-secondary/20 text-text-secondary',
    };
    return colors[priority] || colors.medium;
  };

  return (
    <div
      onClick={() => navigate(`/projects/${project.id}`)}
      className={`bg-surface rounded-md border border-border border-t-4 ${getConfidenceColor(project.confidence_score)} p-6 cursor-pointer hover:border-primary/50 transition-all shadow-card hover:shadow-lg`}
    >
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-md font-semibold text-text-primary">{project.name}</h3>
        <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(project.priority)}`}>
          {project.priority}
        </span>
      </div>

      <p className="text-sm text-text-secondary mb-4 line-clamp-2">{project.description}</p>

      <div className="flex items-center gap-4 mb-4 text-sm text-text-secondary">
        <div className="flex items-center gap-2">
          <Calendar size={14} />
          <span>{project.deadline}</span>
        </div>
        <div className="flex items-center gap-2">
          <Gauge size={14} />
          <span className={getConfidenceColor(project.confidence_score).replace('border-', 'text-')}>
            {project.confidence_score?.toFixed(2)}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-text-secondary">{project.status}</span>
      </div>
    </div>
  );
};

export default ProjectCard;
