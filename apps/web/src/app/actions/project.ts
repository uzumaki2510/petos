'use server';

import { revalidatePath } from 'next/cache';
import { fetchServerApi } from '@/lib/api/server';

export async function createProjectAction(orgId: string, data: { name: string; description?: string | null }) {
  try {
    const response = await fetchServerApi(`/v1/organizations/${orgId}/projects`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    revalidatePath('/app');
    return { success: true, data: response };
  } catch (error: any) {
    return { success: false, error: error.message || 'Failed to create project' };
  }
}
