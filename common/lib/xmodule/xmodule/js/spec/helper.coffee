# Stub Youtube API
window.YT =
  PlayerState:
    UNSTARTED: -1
    ENDED: 0
    PLAYING: 1
    PAUSED: 2
    BUFFERING: 3
    CUED: 5

jasmine.getFixtures().fixturesPath = 'xmodule/js/fixtures'

jasmine.stubbedMetadata =
  slowerSpeedYoutubeId:
    id: 'slowerSpeedYoutubeId'
    duration: 300
  normalSpeedYoutubeId:
    id: 'normalSpeedYoutubeId'
    duration: 200
  bogus:
    duration: 100

jasmine.stubbedCaption =
  start: [0, 10000, 20000, 30000]
  text: ['Caption at 0', 'Caption at 10000', 'Caption at 20000', 'Caption at 30000']

jasmine.stubRequests = ->
  spyOn($, 'ajax').andCallFake (settings) ->
    if match = settings.url.match /youtube\.com\/.+\/videos\/(.+)\?v=2&alt=jsonc/
      settings.success data: jasmine.stubbedMetadata[match[1]]
    else if match = settings.url.match /static(\/.*)?\/subs\/(.+)\.srt\.sjson/
      settings.success jasmine.stubbedCaption
    else if settings.url.match /.+\/problem_get$/
      settings.success html: readFixtures('problem_content.html')
    else if settings.url == '/calculate' ||
      settings.url.match(/.+\/goto_position$/) ||
      settings.url.match(/event$/) ||
      settings.url.match(/.+\/problem_(check|reset|show|save)$/)
      # do nothing
    else
      throw "External request attempted for #{settings.url}, which is not defined."

jasmine.stubYoutubePlayer = ->
  YT.Player = ->
    obj = jasmine.createSpyObj 'YT.Player', ['cueVideoById', 'getVideoEmbedCode',
    'getCurrentTime', 'getPlayerState', 'getVolume', 'setVolume', 'loadVideoById',
    'playVideo', 'pauseVideo', 'seekTo', 'getDuration', 'getAvailablePlaybackRates', 'setPlaybackRate']
    obj['getAvailablePlaybackRates'] = jasmine.createSpy('getAvailablePlaybackRates').andReturn [0.75, 1.0, 1.25, 1.5]
    obj

jasmine.stubVideoPlayer = (context, enableParts, createPlayer=true) ->
  enableParts = [enableParts] unless $.isArray(enableParts)
  suite = context.suite
  currentPartName = suite.description while suite = suite.parentSuite
  enableParts.push currentPartName

  loadFixtures 'video.html'
  jasmine.stubRequests()
  YT.Player = undefined
  videosDefinition = '0.75:slowerSpeedYoutubeId,1.0:normalSpeedYoutubeId'
  context.video = new Video '#example', videosDefinition
  jasmine.stubYoutubePlayer()
  if createPlayer
    return new VideoPlayer(video: context.video)

jasmine.stubVideoPlayerAlpha = (context, enableParts, createPlayer=true) ->
  suite = context.suite
  currentPartName = suite.description while suite = suite.parentSuite

  loadFixtures 'videoalpha.html'
  jasmine.stubRequests()
  YT.Player = undefined
  window.OldVideoPlayerAlpha = undefined
  context.video = new VideoAlpha '#example', '.75:slowerSpeedYoutubeId,1.0:normalSpeedYoutubeId'
  jasmine.stubYoutubePlayer()
  if createPlayer
    return new VideoPlayerAlpha(video: context.video)


# Stub jQuery.cookie
$.cookie = jasmine.createSpy('jQuery.cookie').andReturn '1.0'

# Stub jQuery.qtip
$.fn.qtip = jasmine.createSpy 'jQuery.qtip'

# Stub jQuery.scrollTo
$.fn.scrollTo = jasmine.createSpy 'jQuery.scrollTo'
