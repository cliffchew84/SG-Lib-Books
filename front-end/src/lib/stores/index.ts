import { writable } from 'svelte/store';
import { libraryStore, libraryAPIStore } from './library';
import { bookStore } from './book';
import { notificationStore } from './notification';

export const isLoading = writable<boolean>(true);
export { libraryStore, libraryAPIStore, bookStore, notificationStore };

