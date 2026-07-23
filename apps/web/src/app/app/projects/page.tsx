import { Metadata } from 'next';
import { getUserOrganizations, getOrganizationProjects } from '@/lib/api/server';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { buttonVariants } from '@/components/ui/button';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Projects | PetOS',
};

export default async function ProjectsPage() {
  let organizations: any[] = [];
  let projects: any[] = [];

  try {
    organizations = await getUserOrganizations();
    if (organizations.length > 0) {
      projects = await getOrganizationProjects(organizations[0].id);
    }
  } catch (error) {
    console.error('Failed to fetch projects:', error);
  }

  const orgId = organizations[0]?.id;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
        {orgId && (
          <Link href={`/app/projects/new`} className={buttonVariants({ size: 'sm' })}>
            New Project
          </Link>
        )}
      </div>

      {projects.length === 0 ? (
        <div className="rounded-md border border-dashed p-8 text-center">
          <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-gray-100">No projects</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
          <div className="mt-6">
            {orgId && (
              <Link href="/app/projects/new" className={buttonVariants()}>
                Create Project
              </Link>
            )}
          </div>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project: any) => (
            <Card key={project.id}>
              <CardHeader>
                <CardTitle>{project.name}</CardTitle>
                <CardDescription className="truncate">
                  {project.description || 'No description'}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <Link href={`/app/projects/${project.id}`} className="text-sm text-primary hover:underline">
                  View Project
                </Link>
                <span className={`text-xs px-2 py-1 rounded-full ${project.status === 'archived' ? 'bg-gray-100 text-gray-500' : 'bg-green-100 text-green-700'}`}>
                  {project.status}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
