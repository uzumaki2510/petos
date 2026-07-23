# UX Vision

## 1. Gamified, Not A Toy
PetOS is a serious software engineering tool presented through a gamified interface. The UX must strike a balance: the pixel art must be engaging, but it should not distract from or obfuscate the actual code diffs, test results, and PRs. 

## 2. Visualizing Backend State
The pixel office is a visualizer. 
- When an agent is "Thinking," they might have a lightbulb icon in the UI.
- When an agent is "Coding," they might animate typing at their desk.
- **Rule:** The frontend UI must *never* dictate what the agent does. It simply listens to WebSocket/SSE events from the backend and animates accordingly.

## 3. High-Fidelity Technical Tools
While the "office" is pixel-art, the technical interfaces (code diff viewer, terminal logs) should look like modern developer tools. Use monospaced fonts, syntax highlighting, and clear red/green diffs. The contrast between the gamified office and the professional code viewer highlights the uniqueness of PetOS.

## 4. The Pet Personas
- **Captain:** Authoritative, organized. Visually represented perhaps as a dog or cat with a captain's hat.
- **ThemeFox:** Creative, energetic. Visually a fox, perhaps holding a paintbrush or surrounded by color palettes.
- **BugDog:** Diligent, focused. Visually a hound or bulldog with a magnifying glass. 
*(Specific sprites to be defined in Phase 5).*
