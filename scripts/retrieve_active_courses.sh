curl -H "Authorization: Bearer $(cat api-key.txt)" "https://fhict.instructure.com/api/v1/courses?per_page=100&enrollment_state=active"

