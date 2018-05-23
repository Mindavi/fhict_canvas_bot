course=5844
curl -H "Authorization: Bearer $(cat api-key.txt)" "https://fhict.instructure.com/api/v1/courses/$course/discussion_topics?per_page=100&only_announcements=true"
