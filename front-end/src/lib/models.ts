import { type MouseEventHandler } from 'svelte/elements';
import type { BookAvail } from './api/models';

export interface Book {
	brn: number;
	title?: string;
	author?: string;
	publishYear?: string;
	callNumber?: string;
	summary?: string;
	imageLink?: string;
	branches?: string[];
	bookmarked: boolean;
	items?: BookAvail[];
}

export interface BookProp extends Book {
	onBookMarked: MouseEventHandler<HTMLButtonElement>;
	bookMarkLoading: boolean;
}

export interface Library {
	name: string;
	onLoanBooks: Book[];
	availBooks: Book[];
	openingHoursDesc: string;
	favourite: boolean;
	imageLink?: string;
	location?: string;
}

export interface LibraryProp extends Library {
	onFavourite: MouseEventHandler<HTMLButtonElement>;
}
