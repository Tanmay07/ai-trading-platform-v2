import { create } from 'zustand';

export const useUIStore = create((set) => ({
  isContextPanelOpen: false,
  contextPanelContent: null, // React node to render inside the panel
  isCommandPaletteOpen: false,

  openContextPanel: (content) => set({ isContextPanelOpen: true, contextPanelContent: content }),
  closeContextPanel: () => set({ isContextPanelOpen: false }),
  
  toggleCommandPalette: () => set((state) => ({ isCommandPaletteOpen: !state.isCommandPaletteOpen })),
  setCommandPaletteOpen: (isOpen) => set({ isCommandPaletteOpen: isOpen }),
}));
