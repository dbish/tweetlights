var curSortType;

function getMoreTweets(){
	console.log(curSortType)
	$.post('/getTweets',{
		'sortType':curSortType
	}).done(function(response){
		console.log(response);
		loadNewTweets(response);
	}).fail(function(){
		console.log('could not contact server');
	});
}

function sortByRetweets(){
	curSortType = 'retweets';
	getMoreTweets();
}

function sortByFavorites(){
	curSortType = 'favorites';
	getMoreTweets();
}

function sortByRecency(){
	curSortType = 'recency';
	getMoreTweets();
}

function saveHighlights(){
	$.post('/saveHighlights', {
		data:JSON.stringify(Array.from(highlights))
	}).done(function(response){
		clearUnsavedHighlights();
	}).fail(function(){
		console.log('failure in saving from server');
	});
}

window.onload = function(){
	//loadTweets();
	curSortType = 'recency';
	loadNewTweets(startingTweets);
};

