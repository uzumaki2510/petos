import { ProjectForm } from '@/components/workspace/project-form';
import { getUserOrganizations } from '@/lib/api/server';
import { redirect } from 'next/navigation';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'New Project | PetOS',
};

export default async function NewProjectPage() {
  let orgId = '';
  try {
    const orgs = await getUserOrganizations();
    if (orgs && orgs.length > 0) {
      orgId = orgs[0].id;
    } else {
      redirect('/app');
    }
  } catch {
    redirect('/app');
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Create a Project</h1>
        <p className="text-muted-foreground mt-2">
          Projects group your resources together.
        </p>
      </div>
      <ProjectForm orgId={orgId} />
    </div>
  );
}
