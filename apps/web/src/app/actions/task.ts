'use server';

import { revalidatePath } from 'next/cache';
import { fetchServerApi } from '@/lib/api/server';

export async function createProjectTask(projectId: string, payload: any) {
  try {
    const data = await fetchServerApi(`/v1/projects/${projectId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    revalidatePath(`/app/projects/${projectId}/tasks`);
    revalidatePath(`/app/projects/${projectId}/board`);
    return { success: true, data };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Failed to create task',
    };
  }
}

export async function transitionProjectTask(taskId: string, projectId: string, payload: any) {
  try {
    const data = await fetchServerApi(`/v1/tasks/${taskId}/transition`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    revalidatePath(`/app/projects/${projectId}/tasks`);
    revalidatePath(`/app/projects/${projectId}/tasks/${taskId}`);
    revalidatePath(`/app/projects/${projectId}/board`);
    return { success: true, data };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Failed to transition task',
    };
  }
}

export async function archiveProjectTask(taskId: string, projectId: string, payload: any) {
  try {
    const data = await fetchServerApi(`/v1/tasks/${taskId}/archive`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    revalidatePath(`/app/projects/${projectId}/tasks`);
    revalidatePath(`/app/projects/${projectId}/tasks/${taskId}`);
    revalidatePath(`/app/projects/${projectId}/board`);
    return { success: true, data };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Failed to archive task',
    };
  }
}

export async function addTaskComment(taskId: string, projectId: string, payload: any) {
  try {
    const data = await fetchServerApi(`/v1/tasks/${taskId}/comments`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    revalidatePath(`/app/projects/${projectId}/tasks/${taskId}`);
    return { success: true, data };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Failed to add comment',
    };
  }
}

export async function addTaskDependency(taskId: string, projectId: string, payload: any) {
  try {
    const data = await fetchServerApi(`/v1/tasks/${taskId}/dependencies`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    revalidatePath(`/app/projects/${projectId}/tasks/${taskId}`);
    return { success: true, data };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || 'Failed to add dependency',
    };
  }
}
