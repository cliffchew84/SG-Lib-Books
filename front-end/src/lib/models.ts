import { type MouseEventHandler } from 'svelte/elements';

export interface Library {
	id: string;
	name: string;
	noOnLoan: number;
	noAvail: number;
	openingHoursDesc: string;
	favourite: boolean;
	imageLink?: string;
}

export interface LibraryProp extends Library {
	onFavourite: MouseEventHandler<HTMLButtonElement>;
}
