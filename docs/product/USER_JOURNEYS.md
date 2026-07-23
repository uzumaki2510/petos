# User Journeys

## Journey 1: Onboarding and Project Creation
1. **User** visits the PetOS web app and signs up.
2. **User** authorizes PetOS via GitHub OAuth.
3. **User** creates a new Project and selects a repository from their GitHub account.
4. **PetOS** initializes the Project, and the user is dropped into the Pixel Office dashboard where Captain, ThemeFox, and BugDog are marked as "Idle".

## Journey 2: Assigning a Task
1. **User** clicks "New Task" and types: *"Update the login button to be a blue gradient with a hover effect."*
2. **User** submits the task.
3. The UI updates: **Captain**'s status changes to "Planning."
4. **Captain** creates a plan and delegates the CSS work to ThemeFox.
5. **ThemeFox**'s status changes to "Writing Code."
6. The user can watch a real-time activity feed showing terminal logs and file modifications happening in the background sandbox.

## Journey 3: Review and Pull Request
1. **ThemeFox** finishes the code. **Captain** assigns **BugDog** to verify it.
2. **BugDog**'s status changes to "Running Tests."
3. Once tests pass, the system prompts the **User** with a "Review Required" notification.
4. **User** opens the Code-Diff viewer to see the changes made to the CSS file.
5. **User** clicks "Approve & Create PR."
6. **PetOS** automatically creates a Pull Request on GitHub. The pets return to an "Idle" state.
