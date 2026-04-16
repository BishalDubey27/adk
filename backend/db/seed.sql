-- Seed data for Tech Sarathi development
-- NOTE: skill_embedding values are NOT included here.
-- After seeding, run: POST /api/v1/team/refresh-all-embeddings
-- to generate real embeddings via Vertex AI / Gemini API.

-- Insert team members (without embeddings — will be generated via API)
INSERT INTO team_members (id, name, email, role, skills, availability_hours_per_week, current_load_hours) VALUES
('11111111-1111-1111-1111-111111111111', 'Sahil Prajapati', 'sahil@techsarathi.com', 'Full Stack Developer', ARRAY['Python', 'React', 'FastAPI', 'PostgreSQL'], 40, 20),
('22222222-2222-2222-2222-222222222222', 'Amit Yadav', 'amit@techsarathi.com', 'AI/ML Engineer', ARRAY['Python', 'TensorFlow', 'AI', 'Machine Learning'], 40, 15),
('33333333-3333-3333-3333-333333333333', 'Khush Patel', 'khush@techsarathi.com', 'Frontend Developer', ARRAY['React', 'TypeScript', 'UI/UX', 'Tailwind'], 40, 25),
('44444444-4444-4444-4444-444444444444', 'Bishal Dubey', 'bishal@techsarathi.com', 'Backend Developer', ARRAY['Python', 'FastAPI', 'Database', 'Cloud'], 40, 10)
ON CONFLICT (id) DO NOTHING;

-- Insert a sample project
INSERT INTO projects (id, name, description, status, priority, deadline, pm_id, confidence_score) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'E-commerce Platform', 'Build a modern e-commerce platform with AI-powered recommendations', 'active', 'high', '2026-06-30', '44444444-4444-4444-4444-444444444444', 0.87)
ON CONFLICT (id) DO NOTHING;

-- Insert sample tasks
INSERT INTO tasks (id, project_id, title, description, status, assigned_to, estimated_hours, due_date, risk_score) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Setup Project Infrastructure', 'Initialize repository and CI/CD pipeline', 'done', '44444444-4444-4444-4444-444444444444', 8, '2026-05-01', 0.1),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Design Database Schema', 'Create ERD and database schema', 'in_progress', '44444444-4444-4444-4444-444444444444', 16, '2026-05-10', 0.2),
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Build Product Catalog API', 'REST API for product management', 'todo', '11111111-1111-1111-1111-111111111111', 24, '2026-05-20', 0.3),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Implement AI Recommendations', 'ML model for product recommendations', 'todo', '22222222-2222-2222-2222-222222222222', 32, '2026-06-01', 0.4),
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Design UI Components', 'Create reusable React components', 'in_progress', '33333333-3333-3333-3333-333333333333', 20, '2026-05-15', 0.2)
ON CONFLICT (id) DO NOTHING;

-- Insert sample audit log entry
INSERT INTO audit_log (id, agent_name, action, entity_type, entity_id, confidence_score, output_data) VALUES
('99999999-9999-9999-9999-999999999999', 'execution_coordinator', 'project_created', 'project', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 0.87, '{"action": "auto_proceed", "tasks_created": 5}')
ON CONFLICT (id) DO NOTHING;
