// Generated by CoffeeScript 1.8.0
(function() {
  var commands;

  commands = {
    INFO: function(m) {
      return console.log(m);
    },
    VISIT: function(m) {
      var $line, line, pipe, site, site_filter;
      if ($('table.last').size()) {
        pipe = m.indexOf('|');
        site = m.substr(0, pipe);
        line = m.substr(pipe + 1);
        $line = $(line);
        site_filter = $('table.last').attr('data-site');
        if (site_filter === 'all' || site.indexOf(site_filter) > -1) {
          $line.addClass('active');
          $line.addClass('recent');
          $('table.last tbody').prepend($line);
          setTimeout((function() {
            return $line.removeClass('recent');
          }), 500);
        }
      }
      $('header h1 a').addClass('pulse');
      return setTimeout((function() {
        return $('header h1 a').removeClass('pulse');
      }), 75);
    },
    EXIT: function(uuid) {
      return $("table.last tr[data-visit-uuid=" + uuid + "]").removeClass('active');
    }
  };

  $(function() {
    var host, last_visit_ws;
    host = location.host;
    if (host.indexOf(':')) {
      host = host.split(':')[0];
    }
    window.last_visit_ws = last_visit_ws = new WebSocket((location.protocol === 'https:' ? "wss://" + host : "ws://" + host + ":" + window._pystil_port) + "/last_visits");
    last_visit_ws.onopen = function() {
      return console.log('Last visits websocket opened', arguments);
    };
    last_visit_ws.onerror = function() {
      return console.log('Last visits websocket errored', arguments);
    };
    return last_visit_ws.onmessage = function(evt) {
      var cmd, data, message, pipe;
      message = evt.data;
      pipe = message.indexOf('|');
      if (pipe > -1) {
        cmd = message.substr(0, pipe);
        data = message.substr(pipe + 1);
        return commands[cmd](data);
      }
    };
  });

}).call(this);
