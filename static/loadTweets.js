function loadTweets(){
	console.log("loading tweets");

	var tweets = jQuery(".tweet");
	console.log(tweets);

	jQuery(tweets).each( function( t, tweet ) { 

	    var id = jQuery(this).attr('id'); 
	    console.log(id);
	    console.log(tweet);
	    twttr.widgets.createTweet(
	      id, tweet, 
	      {
		conversation : 'none',    // or all
		cards        : 'hidden',  // or visible 
		linkColor    : '#cc0000', // default is blue
		theme        : 'light'    // or dark
	      });

	    });
}
