var curSortType;
var index = 10;

function getTweets(idx){
	console.log(curSortType)
	console.log(idx);
	$.post('/getTweets',{
		'sortType':curSortType,
		'index':idx
	}).done(function(response){
		console.log(response);
		loadNewTweets(response['tweets']);
		index = response['index'];
	}).fail(function(){
		console.log('could not contact server');
	});
}

function getMoreTweets(){
	getTweets(index);
}

function sortByRetweets(){
	$('#previousTweets').empty();
	curSortType = 'retweets';
	getTweets(0);
}

function sortByFavorites(){
	$('#previousTweets').empty();
	curSortType = 'favorites';
	getTweets(0);
}

function sortByRecency(){
	$('#previousTweets').empty();
	curSortType = 'recency';
	getTweets(0);
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

