import { writable } from "svelte/store";
import type { Book, Library } from "$lib/models";

export const bookStore = writable<{ [key: number]: Book }>({})
export const libraryStore = writable<Library[]>([])
