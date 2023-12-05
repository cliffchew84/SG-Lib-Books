
@app.get("/lib_events_base", response_class=HTMLResponse)
async def show_library_events(request: Request,
                              page: int = 1,
                              lib: str = "Online",
                              db=Depends(get_db),
                              username=Depends(manager)):

    lib_events = m_db.mg_query_lib_events_by_lib(db, lib)
    today = str(datetime.now().date())

    final_output = list()
    for events in lib_events:
        event_date = events.get('start').split("T", 1)[0]
        if event_date >= today:
            final_output.append(events)

    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    total_records = len(final_output)
    records = final_output[start_index: end_index]
    # total_pages = calculate_total_pages(len(final_output))
    # pagination_links = get_page_links(page, total_pages)

    return templates.TemplateResponse("m_lib_events.html", {
        "request": request,
        "username": username.get("UserName"),
        "lib_events": records,
        # "pagination": pagination_links,
        "total_records": total_records,
        'lib_locations': lib_locations,
        "selected_lib": lib
    })


@app.get("/lib_events", response_class=HTMLResponse)
async def show_lib_events(request: Request,
                          lib: str,
                          page: int = 1,
                          db=Depends(get_db),
                          username=Depends(manager)):

    # Filter for online events first
    lib_events = m_db.mg_query_lib_events_by_lib(db, lib)
    today = str(datetime.now().date())

    final_output = list()
    for events in lib_events:
        event_date = events.get('start').split("T", 1)[0]
        if event_date >= today:
            final_output.append(events)

    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    total_records = len(final_output)

    records = final_output[start_index: end_index]
    # total_pages = calculate_total_pages(len(final_output))
    # pagination_links = get_page_links(page, total_pages)

    return templates.TemplateResponse("m_lib_events_table.html", {
        "request": request,
        "username": username.get("UserName"),
        "lib_events": records,
        # "pagination": pagination_links,
        "total_records": total_records,
        'lib_locations': lib_locations,
        "selected_lib": lib
    })
