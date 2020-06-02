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
		loadTweets(response['tweets'], 'previousTweets');
		index = response['index'];
	}).fail(function(){
		console.log('could not contact server');
	});
}

function getMoreTweets(){
	getTweets(index);
}

function sortByRetweets(){
	makeActive('#retweetsButton');
	$('#previousTweets').empty();
	curSortType = 'retweets';
	getTweets(0);
}

function sortByFavorites(){
	makeActive('#favoritesButton');
	$('#previousTweets').empty();
	curSortType = 'favorites';
	getTweets(0);
}

function sortByRecency(){
	makeActive('#recencyButton');
	$('#previousTweets').empty();
	curSortType = 'recency';
	getTweets(0);
}

function sortByScore(){
	makeActive('#scoreButton');
	$('#previousTweets').empty();
	curSortType = 'score';

	getTweets(0);
}

function makeActive(id){
	$('.btn-outline-dark.active').prop('aria-pressed', false);
	$('.btn-outline-dark.active').removeClass('active');
	$(id).prop('aria-pressed', true);
	$(id).addClass('active');
}

function addFlash(text){
	var flashes = $('#flashes');
	var newFlash = $(document.createElement('div'));
	newFlash.addClass('alert alert-info alert-dismissable fade show');
	newFlash.attr('role', 'alert');
	newFlash.append(text);
	var closeButton = $(document.createElement('button'));
	closeButton.attr('type', 'button');
	closeButton.addClass('close');
	closeButton.attr('data-dismiss', 'alert');
	closeButton.attr('aria-label', 'Close');
	closeButton.append('<span aria-hidden="true">&times;</span>');
	newFlash.append(closeButton);
	flashes.append(newFlash);
}

function saveHighlights(){
	$.post('/saveHighlights', {

		//data:JSON.stringify(Array.from(highlights)),
		'add':JSON.stringify(Array.from(highlightsToAdd)),
		'remove':JSON.stringify(Array.from(highlightsToRemove))
	}).done(function(response){
		addFlash('saved');
		clearUnsavedHighlights();
	}).fail(function(){
		console.log('failure in saving from server');
	});
}

function copyToClipboard(text){
	console.log(text);
	var copyText = document.getElementById('externalLink');
	console.log(copyText);
	copyText.focus()
	console.log(copyText.value);
	copyText.setSelectionRange(0, copyText.value.length)
	console.log(copyText.textContent);
	console.log(copyText.value);
	result = document.execCommand('copy');
	console.log(result);
}

window.onload = function(){
	//loadTweets();
	curSortType = 'recency';
	loadHighlightTweets(collectionTweets, 'tweets');
	loadTweets(startingTweets, 'previousTweets');
	$('#saveButton').prop('disabled', true);

	var tweetIDSearch = document.getElementById('tweetID');
	tweetIDSearch.addEventListener("keyup", function(event){
		if (event.keyCode === 13){
			event.preventDefault();
			document.getElementById('searchButton').click();
		}
	});

};

