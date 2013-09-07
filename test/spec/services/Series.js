'use strict';

var $httpBackend;

describe('Service: Series', function () {

  // load the service's module
  beforeEach(module('tvcalApp'));

  // instantiate service
  var Series;
  beforeEach(inject(function (_Series_) {
    Series = _Series_;
  }));
  
  beforeEach(inject(function ($injector) {
      var url_get = '/search/The%20Simpsons';

      var response_get = [{"seriesid": "71663", "lid": 7, "network": "FOX", "language": "en", "zap2it_id": "EP00018693", "overview": "Set in Springfield, the average American town, the show focuses on the antics and everyday adventures of the Simpson family; Homer, Marge, Bart, Lisa and Maggie, as well as a virtual cast of thousands. Since the beginning, the series has been a pop culture icon, attracting hundreds of celebrities to guest star. The show has also made name for itself in its fearless satirical take on politics, media and American life in general.", "imdb_id": "tt0096697", "seriesname": "The Simpsons", "firstaired": "1989-12-17", "banner": "graphical/71663-g24.jpg", "id": 71663}, {"seriesid": "153221", "lid": 7, "network": "VH1", "language": "en", "overview": "Jessica Simpson is embarking on a world tour...but this time it has nothing to do with music. Jessica, along with her two best friends, Ken Paves and CaCee Cobb, are traveling the globe to explore how different cultures define beauty and the extraordinary lengths that women will go to in order to achieve it. \n\nJourneying from Tokyo and Thailand, to Paris and Rio, to Uganda, Morocco and India -- the cast is met in each city by a \"beauty ambassador\" who helps them tackle topics revolving around fashion, fitness, diet and outlandish spa treatments. In each country, Jessica, Ken and CaCee experience firsthand some of the local beauty rituals, from drinking cow urine in India, to being buried up to their necks in Tokyo, to drinking gourds of ghee in a fattening hut in Uganda. But it's not all fun and games -- Jessica also explores the high price that some women pay to feel beautiful. Imagine the plight of women in Northern Thailand, who wear 20-pound rings around their necks, crushing their clavicles, to a mother in Rio who cannot afford electricity, but is secretly saving for butt implants. \n\nEach episode ends in a complete transformation of the cast. Imagine Jessica, Ken and CaCee dressed in ornate kaftans, or camel-back riding to a festive Moroccan party complete with belly dancers and live musicians. \n\nAs Jessica learns how beauty is defined across the globe, and how she \"measures up,\" and her own definition of the word, she is challenged to redefine it along the way, allowing the audience to see a personal, vulnerable and oftentimes hilarious side of Jessica Simpson. \n\nEach episode culminates in a complete transformation of the cast -- Imagine Jessica, Ken and CaCee dressed in ornate kaftans, riding camel-back to a festive Moroccan party, complete with belly dancers and live musicians. They talk to local women and dance the night away Moroccan style. \n\nAs Jessica learns how beauty is defined in far away lands, her own sense of beauty, and how she \"measures up\" is challenged and redefined along the way, allowing the audience to see a personal, and often times, vulnerable and hilarious side of Jessica Simpson. ", "seriesname": "Jessica Simpson's The Price of Beauty", "banner": "graphical/153221-g.jpg", "id": 153221}]

      $httpBackend = $injector.get('$httpBackend');

      $httpBackend.whenGET(url_get).respond(response_get);

  }));

  it('should have a query method', function () {
    expect(Series.query);
  });
  
  it('should return a list if search for The Simpsons', function () {
	  var res = Series.query({search: 'The Simpsons'});
	  $httpBackend.flush();
	    expect(res[0].seriesid === 71663);
	  });

});
