import { type MouseEventHandler } from 'svelte/elements';

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
}

export interface BookProp extends Book {
	onBookMarked: MouseEventHandler<HTMLButtonElement>;
}

export interface Library {
	id: string;
	name: string;
	noOnLoan: number;
	noAvail: number;
	openingHoursDesc: string;
	favourite: boolean;
	imageLink?: string;
	location?: string;
}

export interface LibraryProp extends Library {
	onFavourite: MouseEventHandler<HTMLButtonElement>;
}
