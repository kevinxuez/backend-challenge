# Open-Ended Questions

## 1.

1st: The user model would need to be reworked by adding a password field that they need to input. With this password field, it probably should be inputted as a String of text but then hashing somehow by scrambling the info when it's left in the data field to prevent people losing data. 
-hashlib?
2nd: An session state would probably have to be implemented. I originally thught of simply storing that as another user model field but found that there exists functions on Flask that relate to sessions so I'd be using that. this way, we can make sure all users on are verified
-Flask-Session would be really useful
3rd: I'd need to rework the API requests for users to only implement changes for their own userData unless an user has a "admin" role. I'd also need to implement a "owner" and "board" feature onto clubs so that only users who are high-up on the club can access the updateClubInfo API route
4th: There is additional multi-factor verification, token/cookie stuff, and actual cybersecurity protocols that exist and owuld be useful, but I'm not knowledgeable about

## 2.

1st: There'd probably exist a Comments model that would store information on every singular comment. This model would have "title: String", "bodyText: String", "commentID: int (would be unique)", "previousComment:int(if 0 it just means there's no previous comment)", "nextComment:int(if 0 means no next Comment)", "speaker: relationship table with Users (this way you can see comment history)", and "date: datetime (for organizing which comments to display first)"
2nd: I'd have to rework users to have a "comments" relationship table as well, because it's a two way street. It's a one to many table, so this part is pretty important.
3rd: In order to actually instantiate comments, I'd first have to implement part of the systems in question 1 that allow the app to keep track of which "user" is currently accessing it. then, there'd exist a API route to add a comment. This would create a new comment object with a unique commentID (probably randomly generated), bodytext, title, date (current datetime), and an 0 previousComment and nextComment fields. Additionally, this API route would add to the user-comment relationship by adding that user X has made comment Y to the table.
4th: There'd also exist a "reply" API route that (requires an previous comment as input) that does much of what was mentioned above, but it'd have the previous comments commentID in the "previousComment" field. Additionally, the previous comment's "nextComment" field would be replace with the new comment's ID.
5th: this could probably be displayed under the club info if retrieviing info, and ordered by most recent comments (but display comment chains by recursively going from nextComment first)

## 3.
1st: /api/clubs GET, /api/clubs/search GET, /api/users GET are the prime candidates because clubs and user data will be relatively static meaning that the lack of full-table scans wouldn't hurt data integrity as much. /api/tags/<tag_name> GET and api/clubs/<club_code>/favoritedBy GET would also be nice
2nd: Cache invalidation could be solved by creating functions to purge the info of caches (such as a purgeClubCache) if a attached datatable is modified/created/deleted. It'd probably be done by just attaching these functions to the API calls themself
3rd: Additional cache management could involve setting up a time-limit on cached entries so they expire automatically after a certain time and adding granularity for functions such as the search route so it doesn't invalidate every key, instead only the ones as part of the search
4th: I'd probably use Flask packages such as Flask-Caching with a caching backend (at this point I'm searching this stuff up btw I'm not that experienced with this)

