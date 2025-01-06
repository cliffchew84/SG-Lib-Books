set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$begin
  insert into public.users ("UserName", "latest_login", "registered_time", "email_address")
  VALUES (
  	new.email,
  	cast(extract(epoch from new.last_sign_in_at) as integer),
  	cast(extract(epoch from new.created_at) as integer),
  	new.raw_user_meta_data ->> 'name'
	) ON CONFLICT DO NOTHING;
  return new;
end;$function$
;


