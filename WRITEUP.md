# Open-Ended Questions

## 1.

1st: The user model would need to be reworked by adding a password field that they need to input. With this password field, it probably should be inputted as a String of text but then hashing somehow by scrambling the info when it's left in the data field to prevent people losing data. Hashlib could be used here

2nd: An session state would probably have to be implemented. There exists functions on Flask that relate to sessions so I'd be using that. this way, we can make sure all users on are verified and logged in when accessing certain routes. Flask-Session would be a package that I'd use to implement this.

3rd: I'd need to rework the API requests for users to only implement changes for their own userData unless an user has a "admin" role. I'd also need to implement a "owner" and "board" feature onto clubs so that only users who are high-up on the club can access the updateClubInfo API route

4th: I'd want to have a "logout" API route that would clear the session data and make sure the user is logged out. Additionally, there'd be a "currentUser" API route that returns the user data of the current user logged in.

5th: There would be a trackable history of login attempts and password changes that would be stored in a separate table that would have a relationship with users. This way, if there are any suspicious activities, the admin can look at the history and see if there are any red flags.

## 2.

1st: I already have a review system posted. A comment system could be implemented as a follow-up to reviews, allowing users (and people in the club as well) to respond to reviews and have threaded conversations.
2nd: There'd be a comments model that would contain many of the same fields as reviews, but it'd also have a "parentReview" field that would be a foreign key to the review that the comment is associated with. Additionally, there'd be a "parentComment" field that would be a foreign key to the comment that the comment is replying to (if it's a reply). This way, we can have multiple threaded conversations under a single review.
3rd: In order to actually instantiate comments, I'd have an API route /api/reviews/<reviewId>/comments POST that takes in the comment text, userId, and optionally a previousCommentId (if it's a reply). The route would then create a new comment in the database with the appropriate fields filled out. The response would be the created comment object.
4th: This comment could probably be displayed under the club info when retrieving info, and ordered by most recent comments
5th: A comment should ultimately be many-to-one with users (a user can have many comments, but a comment can only have one user) and many-to-one with reviews (a review can have many comments, but a comment can only be associated with one review). 

## 3.
1st: /api/clubs GET, /api/clubs/search GET, /api/users GET are the prime candidates because clubs and user data will be relatively static meaning that the lack of full-table scans wouldn't hurt data integrity as much. /api/tags/<tag_name> GET and api/clubs/<club_code>/favoritedBy GET would also be nice. 
2nd: Cache invalidation could be solved by creating functions to purge the info of caches (such as a purgeClubCache) if a attached datatable is modified/created/deleted. It'd probably be done by just attaching these functions to the API calls themself
3rd: Additional cache management could involve setting up a time-limit on cached entries so they expire automatically after a certain time and adding granularity for functions such as the search route so it doesn't invalidate every key, instead only the ones as part of the search
4th: I'd probably use Flask packages such as Flask-Caching to implement and serve as a caching backend

