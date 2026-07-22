import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  isAdmin: true, // Defaulting to true for demo purposes
  userProfile: {
    name: 'Jane Doe',
    role: 'Chief Investment Officer',
    avatar: 'https://ui-avatars.com/api/?name=Jane+Doe&background=58a6ff&color=fff',
  },
  toggleAdmin: () => set((state) => ({ isAdmin: !state.isAdmin })),
}));
