<div ng-controller='SearchController as searchCtrl'>
	<div class="row">
		<div id="imaginary_container">
			<div class="input-group stylish-input-group">
				<input type="text" ng-model="searchCtrl.inputTerm" ng-init="searchCtrl.inputTerm=''" class="form-control" placeholder="Search video"
				ng-keypress="searchCtrl.goToSearch($event, searchCtrl.inputTerm)">
				<span class="input-group-addon">
					<a href ui-sref="logged.search({q: searchCtrl.inputTerm})">
						<button><span class="glyphicon glyphicon-search"></span></button>
					</a>
				</span>
			</div>
		</div>
	</div>
</div>
<hr/>
<div
	ng-if="datactrl.loading"
	ng-include="main.templateDir + 'loader.html'">
</div>
<div ng-controller='WatchController as watchCtrl' id="video-wrapper">
	<div class="row">
		<div class="col-xs-12 col-md-6">
			<div style="float: left; width: 100%">
				<video id="videoarea" ng-src="{{watchCtrl.video.links['content'] | trustUrl }}" preload="none" type="video/mp4" controls></video>
				<div class="container" ng-show="watchCtrl.showmeli" style="float: left; width: 100%"><br></br><span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span> Loading...</div>
			</div>
			<div class="scrollmenu" style="float: left;">
				<a ng-repeat="item in watchCtrl.items" style="width: 13%;" scroll-on-click>
					<img style="width: 90%; height: 90%" id="{{item[0]}}" duration="{{item[1]}}" nshots="{{item[2]}}" shotd="{{item[3]}}" progr="{{item[4]}}" timestamp="{{item[5]}}" ng-src="{{item[6]}}" />
				</a>
			</div>

			<!-- <div uib-carousel interval="5000" class="scrollmenu" style="float:left; width:100%;" active="active">
            <div uib-slide ng-repeat="item in watchCtrl.items" index="$index" style="width: 13%;">

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index][0]}}" duration="{{watchCtrl.items[$index][1]}}" nshots="{{watchCtrl.items[$index][2]}}" shotd="{{watchCtrl.items[$index][3]}}" progr="{{watchCtrl.items[$index][4]}}" timestamp="{{watchCtrl.items[$index][5]}}" ng-src="{{watchCtrl.items[$index][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+1][0]}}" duration="{{watchCtrl.items[$index+1][1]}}" nshots="{{watchCtrl.items[$index+1][2]}}" shotd="{{watchCtrl.items[$index+1][3]}}" progr="{{watchCtrl.items[$index+1][4]}}" timestamp="{{watchCtrl.items[$index+1][5]}}" ng-src="{{watchCtrl.items[$index+1][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+2][0]}}" duration="{{watchCtrl.items[$index+2][1]}}" nshots="{{watchCtrl.items[$index+2][2]}}" shotd="{{watchCtrl.items[$index+2][3]}}" progr="{{watchCtrl.items[$index+2][4]}}" timestamp="{{watchCtrl.items[$index+2][5]}}" ng-src="{{watchCtrl.items[$index+2][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+3][0]}}" duration="{{watchCtrl.items[$index+3][1]}}" nshots="{{watchCtrl.items[$index+3][2]}}" shotd="{{watchCtrl.items[$index+3][3]}}" progr="{{watchCtrl.items[$index+3][4]}}" timestamp="{{watchCtrl.items[$index+3][5]}}" ng-src="{{watchCtrl.items[$index+3][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+4][0]}}" duration="{{watchCtrl.items[$index+4][1]}}" nshots="{{watchCtrl.items[$index+4][2]}}" shotd="{{watchCtrl.items[$index+4][3]}}" progr="{{watchCtrl.items[$index+4][4]}}" timestamp="{{watchCtrl.items[$index+4][5]}}" ng-src="{{watchCtrl.items[$index+4][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+5][0]}}" duration="{{watchCtrl.items[$index+5][1]}}" nshots="{{watchCtrl.items[$index+5][2]}}" shotd="{{watchCtrl.items[$index+5][3]}}" progr="{{watchCtrl.items[$index+5][4]}}" timestamp="{{watchCtrl.items[$index+5][5]}}" ng-src="{{watchCtrl.items[$index+5][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+6][0]}}" duration="{{watchCtrl.items[$index+6][1]}}" nshots="{{watchCtrl.items[$index+6][2]}}" shotd="{{watchCtrl.items[$index+6][3]}}" progr="{{watchCtrl.items[$index+6][4]}}" timestamp="{{watchCtrl.items[$index+6][5]}}" ng-src="{{watchCtrl.items[$index+6][6]}}" style="float:left;" scroll-on-click/>

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+7][0]}}" duration="{{watchCtrl.items[$index+7][1]}}" nshots="{{watchCtrl.items[$index+7][2]}}" shotd="{{watchCtrl.items[$index+7][3]}}" progr="{{watchCtrl.items[$index+7][4]}}" timestamp="{{watchCtrl.items[$index+7][5]}}" ng-src="{{watchCtrl.items[$index+7][6]}}" style="float:left;" scroll-on-click/> 

            <img style="width: 90%; height: 90%" id="{{watchCtrl.items[$index+8][0]}}" duration="{{watchCtrl.items[$index+8][1]}}" nshots="{{watchCtrl.items[$index+8][2]}}" shotd="{{watchCtrl.items[$index+8][3]}}" progr="{{watchCtrl.items[$index+8][4]}}" timestamp="{{watchCtrl.items[$index+8][5]}}" ng-src="{{watchCtrl.items[$index+8][6]}}" style="float:left;" scroll-on-click/> 

            </div>
            </div> -->
		</div>
		<div class="col-xs-12 col-md-6">
			<!-- metadata -->
			<ul><li>
			<div class="primary-description">
				<span class="title">{{watchCtrl.video.attributes.identifying_title}}</span><i>({{watchCtrl.video.relationships.item[0].attributes.duration | parseNum}})</i>
				<p><b>Movie Description</b>:
				<span ng-repeat="description in watchCtrl.video.relationships.descriptions">
				</br>{{description.attributes.text}}{{$last ? '' : ', '}}</br></span></p>
				<p><b>Keywords</b>: <span ng-repeat="keyword in watchCtrl.video.relationships.keywords">
				{{keyword.attributes.term}}{{$last ? '' : ', '}}</span></p>
			</div>
			<div class="secondary-description" ng-show="v.id === ctrl.selectedVideoId">
				<p><b>Production Year(s)</b>: {{watchCtrl.video.attributes.production_years[0] || 'Not available'}}</p>
				<p><b>Location</b>: {{watchCtrl.video.relationships.coverages[0].attributes.spatial[0] || 'Not available'}}</p>
				<p><b>Owner</b>: {{watchCtrl.video.relationships.record_sources[0].attributes.provider_name || 'Not available'}} - <a target="_blank" href="{{watchCtrl.video.relationships.record_sources[0].attributes.is_shown_at || '#'}}">{{watchCtrl.video.relationships.record_sources[0].attributes.is_shown_at || 'Not available'}}</a></p>
				<p><b>Copyright</b>: {{watchCtrl.video.attributes.rights_status || 'Not available'}}</p>
			</div>
			<button type="button" class="btn btn-default pull-right" ng-show="watchCtrl.showmesb" ng-click="watchCtrl.showStoryboard('lg', '.sb-modal-parent')">
			Storyboard <span class="glyphicon glyphicon-book"></span>
			</button>
			</li>
			</ul>
			<div class="sb-modal-parent"></div>
		</div>
	</div>
	<!-- <div class="row">
			<div id="timeline-graph">
					<div google-chart chart="videoTimeline" agc-on-select="jumpToShot(selectedItem)" style="{{videoTimeline.cssStyle}}"/>
					</div>
			</div>
	</div> -->
	<hr/>
	<div ng-controller="MapController as vm" ng-init="vm.init(watchCtrl.video.relationships.coverages[0].attributes.spatial[0])">
	<div class="row">
		<div map-lazy-load="https://maps.google.com/maps/api/js" map-lazy-load-params="{{vm.googleMapsUrl}}" class="col-xs-12">
			<ng-map id="videomap" center="{{vm.videolat}}, {{vm.videolng}}" zoom="{{vm.zoom}}">
			<marker position="[{{vm.videolat}}, {{vm.videolng}}]"  title="{{vm.locname}}" animation="Animation.BOUNCE"></marker>
			</ng-map>
		</div>
	</div>
	</div>
	<hr/>

	<!-- modal content -->
	<script type="text/ng-template" id="myModalContent.html">
	<div modal-movable>
		<button type="button" class="close" ng-click="$ctrl.cancel()" style="padding: 2px 6px;">x</button>
	    <div class="modal-header">
	        <h3 class="modal-title" align="center">Video Storyboard</h3>
	        </br>
	    </div>
	    <div class="modal-body">
	        <form>
	    	<div>
	    	<table class="table">
	    		<tr>
	    			<th>Video Summary<img style="width: 70%; height: 50%; float: right;" ng-src="{{$ctrl.summary}}" ng-click="$ctrl.showSummary()"></th>
				</tr>
			</table>

			<table class="table">
			    <tr>
					<th>Frame number</th>
                    <th>Shot number</th>
				    <th>Frame range</th>
				    <th>Shots</th>
				    <th>Shot timecode</th>
			        <th>Shot duration (sec)</th>
				    <th style="text-align: center">Camera motion</th>
				</tr>

				<div class="storyboard">
				<tr ng-repeat="shot in $ctrl.shots">
                    <td data-title="'Number'" align="center">{{shot.number}}</td>
					<td data-title="'Frame Range'" align="center">{{shot.framerange}}</td>
	       			<td data-title="'Shot'" scroll-on-click>
	           		<img style="width: 40%;" id="{{shot.id}}" duration="{{shot.duration}}" nshots="{{shot.nshots}}" shotd="{{shot.shotd}}" progr="{{shot.progr}}" timestamp="{{shot.timestamp}}" ng-src="{{shot.thumb}}"></td>
	       			<td data-title="'Timestamp'" align="center">{{shot.timestamp}}</td>
	       			<td data-title="'Duration'" align="center">{{shot.duration}}</td>
	       			<td data-title="'Camera motion'" align="center">
	       			<dl class="dl-horizontal">
	       				<div ng-repeat="(e_attr, e_val) in shot.camera | salientEstimates:0.5">
	       					<dt>{{e_attr}}:</dt><dd>{{e_val}}</dd>
	       				</div>
	       			</dl>
	       			</td>
				</tr>
				</div>
			</table>

			</div>
	        </form>
	    </div> <!-- body -->

	    <div class="modal-footer">
	        <button class="btn btn-warning" type="button" ng-click="$ctrl.cancel()">Cancel</button>
	     </div>
	</script>
	</div>

	<script type="text/ng-template" id="summary.html">
	    <div class="modal-header">
	    	<button type="button" class="close" ng-click="$ctrl.cancel()" style="padding: 2px 6px;">x</button>
	       	<h3 class="modal-title" align="center">Video Summary</h3>
	    </div>
	    <div class="modal-body" style="height: 150px;">
	    	<form><div>
	    		<img style="width: 100%; height: 100%; float: right;" ng-src="{{$ctrl.summary}}">
	      	 </div></form>
	    </div>
	</script>
</div>

<!-- modal content -->
<script type="text/ng-template" id="pagination.html">
    <div class="pagination">
    <ul>
  		<li ng-class="{disabled: noPrevious()}"><a ng-click="selectPrevious()">Previous</a></li>
  		<li ng-repeat="page in pages" ng-class="{active: isActive(page)}"><a ng-click="selectPage(page)">{{page}}</a></li>
  		<li ng-class="{disabled: noNext()}"><a ng-click="selectNext()">Next</a></li>
  	</ul>
	</div>
</script>
