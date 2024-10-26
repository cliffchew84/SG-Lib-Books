alter table "public"."books_avail" add constraint "books_avail_BID_fkey" FOREIGN KEY ("BID") REFERENCES books_info("BID") ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."books_avail" validate constraint "books_avail_BID_fkey";

alter table "public"."user_books" add constraint "user_books_BID_fkey" FOREIGN KEY ("BID") REFERENCES books_info("BID") ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."user_books" validate constraint "user_books_BID_fkey";

alter table "public"."user_books" add constraint "user_books_UserName_fkey" FOREIGN KEY ("UserName") REFERENCES users("UserName") ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."user_books" validate constraint "user_books_UserName_fkey";


