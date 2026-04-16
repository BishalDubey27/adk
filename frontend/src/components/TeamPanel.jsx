import { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { api } from '../api/client';

const TeamPanel = () => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTeam();
  }, []);

  const loadTeam = async () => {
    try {
      const data = await api.team.list();
      setMembers(data.team_members || []);
    } catch (error) {
      console.error('Failed to load team:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCapacityColor = (current, available) => {
    const percentage = (current / available) * 100;
    if (percentage > 90) return 'bg-danger';
    if (percentage > 70) return 'bg-warning';
    return 'bg-success';
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-lg font-semibold text-text-primary">Team</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-primary hover:bg-primary-hover text-white rounded-sm font-semibold transition-colors">
          <Plus size={18} />
          Add Member
        </button>
      </div>

      <div className="space-y-4">
        {members.map((member) => {
          const loadPercentage = (member.current_load_hours / member.availability_hours_per_week) * 100;
          
          return (
            <div key={member.id} className="bg-surface rounded-md p-6 border border-border">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-sm font-semibold text-text-primary">{member.name}</h3>
                    <span className="text-xs text-text-secondary">{member.role}</span>
                  </div>
                  <p className="text-xs text-text-secondary mb-3">{member.email}</p>
                  
                  {member.skills && member.skills.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {member.skills.slice(0, 4).map((skill, idx) => (
                        <span key={idx} className="px-2 py-1 bg-surface-raised text-text-secondary rounded-full text-xs">
                          {skill}
                        </span>
                      ))}
                      {member.skills.length > 4 && (
                        <span className="px-2 py-1 bg-surface-raised text-text-secondary rounded-full text-xs">
                          +{member.skills.length - 4} more
                        </span>
                      )}
                    </div>
                  )}

                  <div className="mb-2">
                    <div className="flex items-center justify-between text-xs text-text-secondary mb-1">
                      <span>Capacity</span>
                      <span>{member.current_load_hours} / {member.availability_hours_per_week} hrs</span>
                    </div>
                    <div className="w-full h-2 bg-surface-raised rounded-full overflow-hidden">
                      <div
                        className={`h-full ${getCapacityColor(member.current_load_hours, member.availability_hours_per_week)} transition-all`}
                        style={{ width: `${Math.min(loadPercentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {members.length === 0 && (
        <div className="text-center py-16 text-text-secondary">
          No team members yet. Add your first team member to get started.
        </div>
      )}
    </div>
  );
};

export default TeamPanel;
