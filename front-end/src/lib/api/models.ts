export interface BookInfo {
	BID: number;
	TitleName?: string;
	Author?: string
	PublishYear?: string;
	Publisher?: string;
	Subjects?: string;
	isbns?: string;
	cover_url?: string;
	summary?: string;
}

export interface BookAvail {
	ItemNo: string;
	CallNumber: string;
	BranchName: string;
	StatusDesc?: string;
	InsertTime?: number
	BID: number;
	DueDate?: string;
	UpdateTime?: string;
}

export interface BookResponse extends BookInfo {
	avails: BookAvail[];
}

export interface Library {
	name: string;
	opening_status: string;
	start_hour?: string;
	end_hour?: string;
	opening_description?: string
	address?: string
	cover_url?: string
}
