import { type MouseEventHandler } from 'svelte/elements';

export interface Library {
	id: string;
	name: string;
	noOnLoan: number;
	noAvail: number;
	openingHoursDesc: string;
	favourite: boolean;
}

export interface LibraryCardProp extends Library {
	onFavourite: MouseEventHandler<HTMLButtonElement>;
	imageLink?: string;
}
