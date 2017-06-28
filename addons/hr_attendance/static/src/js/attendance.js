odoo.define('hr_attendance.hr_attendance', function(require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var formats = require('web.formats');
var Model = require('web.DataModel');
var SystrayMenu = require('web.SystrayMenu');
var time = require('web.time');
var Widget = require('web.Widget');

var _t = core._t;

var AttendanceSlider = Widget.extend({
    template: 'AttendanceSlider',
    init: function (parent) {
        this._super(parent);
        this.set({"signed_in": false});
    },
    start: function() {
        var self = this;
        var tmp = function() {
            var $sign_in_out_icon = this.$('#oe_attendance_sign_in_out_icon');
            $sign_in_out_icon.toggleClass("fa-sign-in", ! this.get("signed_in"));
            $sign_in_out_icon.toggleClass("fa-sign-out", this.get("signed_in"));
        };
        this.on("change:signed_in", this, tmp);
        _.bind(tmp, this)();
        this.$(".oe_attendance_sign_in_out").click(function(ev) {
            ev.preventDefault();
            self.do_update_attendance();
        });
        this.$el.tooltip({
            title: function() {
                var last_text = formats.format_value(self.last_sign, {type: "datetime"});
                var current_text = formats.format_value(new Date(), {type: "datetime"});
                var duration = self.last_sign ? $.timeago(self.last_sign) : "none";
                if (self.get("signed_in")) {
                    return _.str.sprintf(_t("Last sign in: %s,<br />%s.<br />Click to sign out."), last_text, duration);
                } else {
                    return _.str.sprintf(_t("Click to Sign In at %s."), current_text);
                }
            },
        });
        return this.check_attendance();
    },
    validate_transaction_number: function(response, employee_id){
        if(response === false){
            do{
                var res = objBC.GetTmpTransNum(inToken, "", "", "");
                if(res == -1){
                    var try_again_num = confirm("No se pudo obtener la transacción de BioClient [" + objBC.outErrNum + "][" + objBC.outErrMsg + "]" +
                        "Transacción es requerida para la operacion solicitada ¿Desea Reintentar?");
                    if (try_again_num === false){
                        try_trans_num = false;
                        return;
                    }
                }
                else{
                    try_trans_num = false;
                    var inTmpTransNum = objBC.outTmpTransNum;
                    var hr_employee = new data.DataSet(self, 'hr.employee');
                    hr_employee.call('save_transaction_number', [inTmpTransNum, employee_id]);
                    ajax.jsonRpc('/bioflow/set_transaction', 'call', {'lead_id': obj_id, 'transaction': inTmpTransNum});   
                }
            }while(try_trans_num);
        }
        else {
            return response;
        }
    },
    do_update_attendance: function () {
        var self = this;
        GMaps.geolocate({
          success: function(position) {
            console.log('Actualiza');
            // console.log('Geolocaliza');
            var hr_employee = new data.DataSet(self, 'hr.employee');
            var inToken = '';
            var inTmpTransNum = '';
            var inBioKey = '';
            var res = '';
            console.log(! self.get('signed_in'));
            if (!self.get('signed_in')){
                console.log('Entro al if!');
                // Se construye el token
                try {
                    console.log('Construye el token');
                    do{
                        objBC = new ActiveXObject("BioClient.clsBioClient");
                        var res = objBC.GetToken("", "", "");
                        inToken = objBC.outToken;
                        if (res == -1){
                            var try_again = confirm("No se pudo obtener token de BioEngine Client [" + objBC.outErrNum + "][" + objBC.outErrMsg + "]" +
                                "Token es requerido para la aplicacion ¿Desea Reintentar?");
                            if (try_again === false){
                                try_token = false;
                                return;
                            }
                        }
                        else{
                            try_token = false;
                        }
                    }while(try_token);
                }
                catch(err) {
                    alert("No se pudo realizar la conexion con bioengine: " + err.message);
                }
                // Validamos el numero de transaccion
                hr_employee.call('get_transaction_number',[self.employee.id]).done(function(response){
                    inTmpTransNum = self.validate_transaction_number(response, self.employee.id);
                });
                // Solicitamos al usuario sus huellas dactilares
                do{
                    res = objBC.CaptureFinger(
                        inToken,
                        inTmpTransNum,
                        true,
                        false,
                        true,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false,
                        false,
                        "",
                        "");
                    if (res == -1 || (res != -1 && objBC.outErrNum != "0")){
                        var try_again_num = confirm("No se pudo capturar las huellas [" + objBC.outErrNum + "][" + objBC.outErrMsg + "]" +
                            "Huellas son requeridas para el enrolamiento ¿Desea Reintentar?");
                        if (try_again_num === false){
                            try_fingers = false;
                            return;
                        }
                    }
                    else{
                        try_fingers = false;
                    }
                }while(try_fingers);
                // Enviamos paquete biometrico al servidor 
                do{
                    res = objBC.SendToServer(
                        inToken,
                        inTmpTransNum,
                        "",
                        "");
                    if(res == -1){
                            var try_again_sendtoserver = confirm("No se pudo enviar la informacion a bioengine server [" + objBC.outErrNum + "][" + objBC.outErrMsg + "]" +
                                "Envio es Requerido para completar la operación ¿Desea Reintentar?");
                            if (try_again_sendtoserver === false){
                                try_send_toserver = false;
                                return;
                            }
                        }else{
                            try_send_toserver = false;  
                        }
                }while(try_send_toserver);
                // Una vez enviada la informacion buscamos si existe algun guardado con el paquete biometrico anterior
                do{
                    res = objBC.ServerFind(inTmpTransNum, "", "", "", "");
                    if (res == -1 || (res != -1 && objBC.outErrNum != "0"))
                    {
                        var try_again_find = confirm("No se pudo realizar la busqueda [" + objBC.outErrNum + "][" + objBC.outErrMsg + "]" +
                                "La busqueda es requerida ¿Desea Reintentar?");
                        if (try_again_find === false){
                            try_find = false;
                            return;
                        }
                    }else{
                        try_find = false;
                    }
                }while(try_find);
                inBioKey = objBC.outBioKey;
                console.log('Server find - inBioKey: ' + objBC.outBioKey);
                // Si la llave de bioengine nos devuelve vacio, quiere decir que el registro biometrico no existe y podemos enrolarlo
                if (inBioKey !== '') {
                    do{
                        res = objBC.GetAppKey(
                            inBioKey,
                            'Bioflow HSBC',
                            "",
                            "",
                            "");
                        if (res == -1){
                            var try_again_fing = confirm("No se pudo obtener el ID_APLICATIVO [" + objBC.outErrNum + "][" + objBC.outErrMsg + "]" +
                                "¿Desea Reintentar?");
                            if (try_again_fing === false){
                                try_appkey = false;
                                return;
                            }
                        }else{
                            try_appkey = false;
                        }
                   }while(try_appkey);
                    OutAppKey = objBC.OutAppKey;
                    console.log('Get App key - OutAppKey: ' + objBC.OutAppKey);
                    if (OutAppKey !== '') {
                        hr_employee.call('search_res_partner',[OutAppKey]).done(function(response){
                            // -- Cambia estatus cuando encuentra hit y registra la latitud y longitud de la asistencia -- //
                            hr_employee.call('attendance_action_change', [
                                [self.employee.id], position.coords.latitude, position.coords.longitude,
                            ]).done(function (result) {
                                self.last_sign = new Date();
                                self.set({"signed_in": ! self.get("signed_in")});
                            });
                        });
                    } else {
                        alert('El usuario no se encuentra en el sistema');
                    }
                } else {
                    alert('El usuario no esta dentor de la base de datos de bioengine');
                }
            }else{
                console.log('Cayo al else!');
                self.set({"signed_in": ! self.get("signed_in")});
            }
          },
          error: function(error) {
            alert('Geolocation failed: '+error.message);
          },
          not_supported: function() {
            alert("Your browser does not support geolocation");
          },
          always: function() {
            console.log('Done!');
          }
        });
    },
    check_attendance: function () {
        var self = this;
        self.employee = false;
        this.$el.hide();
        var employee = new data.DataSetSearch(self, 'hr.employee', self.session.user_context, [
            ['user_id', '=', self.session.uid]
        ]);
        return employee.read_slice(['id', 'name', 'state', 'last_sign', 'attendance_access']).then(function (res) {
            if (_.isEmpty(res))
                return;
            if (res[0].attendance_access === false){
                return;
            }
            self.$el.show();
            self.employee = res[0];
            self.last_sign = time.str_to_datetime(self.employee.last_sign);
            self.set({"signed_in": self.employee.state !== "absent"});
        });
    },
});

// Put the AttendanceSlider widget in the systray menu if the user is an employee
var Users = new Model('res.users');
Users.call('has_group', ['base.group_user']).done(function(is_employee) {
    if (is_employee) {
        SystrayMenu.Items.push(AttendanceSlider);
    }
});

});
