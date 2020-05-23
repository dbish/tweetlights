var highlights = new Set() 

function getTweet(){
	var tweetID = document.getElementById('tweetID').value;
	var searchTweet = document.getElementById('searchTweet');
	searchTweet.removeChild(searchTweet.firstChild)
	searchTweet.appendChild(createProfileTweet(tweetID));
}

function clearUnsavedHighlights(){
	$(".unsaved").each(function(){
		if ($(this).hasClass('unhighlighted')){
			$(this).remove();
		}else{
			$(this).removeClass('unsaved');
		}
	});
}

function createProfileTweet(id){
	var tweet = document.createElement("div");
	tweet.setAttribute('class', 'tweet');
	tweet.setAttribute('id', id);
	twttr.widgets.createTweet(id, tweet);
	var tweetWrapper = document.createElement("div");
	tweetWrapper.appendChild(tweet);
	tweetWrapper.setAttribute('class', 'shadow p3 mb-5 bg-white rounded');
	tweetWrapper.setAttribute('id', 'wrapper-'+id);
	var button = document.createElement("button");
	button.setAttribute('class', 'btn btn-primary btn-sm');
	button.setAttribute('tweetID', id);
	button.setAttribute('id', 'wrapper-'+id+"-button");
	button.textContent = "+ highlight";
	//button.addEventListener('click', function () {
	//	highlightTweet('wrapper-'+id); 
	//}, false);
	button.addEventListener('click', highlight, false);
	tweetWrapper.appendChild(button);
	return tweetWrapper;
}

function highlight(e){
	var button = e.target;
	var tweetID = button.getAttribute('tweetid');
	console.log(tweetID);
	if (highlights.has(tweetID)){
		console.log('already highlighted');

	} else {
		highlights.add(tweetID);
		//var tweet = $('#wrapper-'+tweetID).clone();
		var tweet = $(createProfileTweet(tweetID));
		var newID = 'wrapper-'+tweetID+'-highlighted';
		tweet.attr('id', newID);
		tweet.addClass('highlighted');
		tweet.addClass('unsaved');
		tweet.find('.btn').remove();

		$("#wrapper-"+tweetID+"-button").hide();

		var button = document.createElement('button');
		button.setAttribute('class', 'btn btn-primary btn-sm');
		button.setAttribute('id', newID+'-button');
		button.setAttribute('tweetID', tweetID);
		button.textContent = 'remove -';
		button.addEventListener('click', unhighlight, false);
		tweet.append(button);

		var highlightTweets = document.getElementById('tweets');
		highlightTweets.append(tweet[0]);
		console.log('done appending');
	}
}

function undodelete(e){
	var tweetID = e.target.getAttribute('tweetid');
	var highlight = $('#wrapper-'+tweetID+'-highlighted')
	highlights.add(tweetID);
	highlight.removeClass('unsaved');
	highlight.addClass('highlighted');
	highlight.removeClass('unhighlighted');
	highlight.find('.btn').remove();

	var button = document.createElement('button');
	button.setAttribute('class', 'btn btn-primary btn-sm');
	button.setAttribute('id', 'wrapper-'+tweetID+'-highlighted-button');
	button.setAttribute('tweetID', tweetID);
	button.textContent = 'remove -';
	button.addEventListener('click', unhighlight, false);
	highlight.append(button);

}

function unhighlight(e){
	var tweetID = e.target.getAttribute('tweetid');
	highlights.delete(tweetID);
	var highlight = $('#wrapper-'+tweetID+'-highlighted')
	$('#wrapper-'+tweetID+'-button').show();
	if (highlight.hasClass('unsaved')){
		highlight.remove();
	}else{
		highlight.addClass('unhighlighted');
		highlight.removeClass('highlighted');
		highlight.addClass('unsaved');
		highlight.find('.btn').remove();
		var button = document.createElement('button');
		button.setAttribute('class', 'btn btn-primary btn-sm');
		button.setAttribute('id', 'wrapper-'+tweetID+'-highlighted-button');
		button.setAttribute('tweetID', tweetID);
		button.textContent = 'undo';
		button.addEventListener('click', undodelete, false);
		highlight.append(button);
		
	}
}

function loadNewTweets(ids){
	var previousTweets = document.getElementById('previousTweets');
	$('#previousTweets').empty();
	var i;
	for (i in ids){
		previousTweets.appendChild(createProfileTweet(ids[i]));
		console.log(ids[i]);
	}
	//twttr.widgets.load("#previousTweets");
}

