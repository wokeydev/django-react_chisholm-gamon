'use strict';

// import dependencies
var gulp = require('gulp'),
    sass = require('gulp-sass'),
    sourcemaps = require('gulp-sourcemaps'),
    rename = require('gulp-rename'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    notify = require('gulp-notify'),
    cleanCSS = require('gulp-clean-css');


// SCSS Compile & minify
gulp.task('build-css', function() {
  return gulp.src('../scss/**/*.scss')
    .pipe(sass({
        includePaths: [
          'node_modules/foundation-sites/scss', // foundation
          'node_modules/motion-ui/src',         // motion ui
          'node_modules/ionicons-npm/scss'      // ionicons
        ]
      }).on('error', sass.logError)
    )
    .pipe(rename({ suffix: '.min' }))
    .pipe(cleanCSS())
    .pipe(gulp.dest('../../static/css'));
});


// Javascript Combine & Minify
gulp.task('build-js', function() {
  return gulp.src([
      './node_modules/echo-js/dist/echo.js',
      './node_modules/infinite-scroll/dist/infinite-scroll.pkgd.js',
      './node_modules/js-cookie/src/js.cookie.js',
      './node_modules/chart.js/dist/Chart.js',
      '../js/app.js',
      '../js/pages/**/*.js'
    ])
    .pipe(uglify().on('error', function(e){
      console.log(e);
    }))
    .pipe(sourcemaps.init())
      .pipe(rename({ suffix: '.min' }))
      .pipe(uglify())
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('../../static/js/'));
});

// watch task
gulp.task('watch', function() {
  gulp.watch('../scss/**/*.scss', ['build-css']);
  gulp.watch('../js/**/*.js', ['build-js']);
});

// default task
gulp.task('default', ['build-css', 'build-js']);
