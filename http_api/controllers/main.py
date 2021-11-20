# -*- coding: utf-8 -*-
from odoo import http
import logging
import urllib3
import json
import pytz
from odoo.addons.mail.controllers.main import MailController
import base64
from datetime import datetime, timedelta, date, timezone
from dateutil.relativedelta import relativedelta
from dateutil import tz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo import api, fields, models, tools, SUPERUSER_ID


from odoo.http import request, route
_logger = logging.getLogger(__name__)


          

class Controller(http.Controller):

   @http.route('/web/session/authenticate/test', type='json', auth="none", withCredentials= 'true')
   def authenticate(self, db, login, password, base_location=None):
      request.session.authenticate(db, login, password)
      result = request.env['ir.http'].session_info()
      vals={
         
         'uid': result['uid'],
         'name': result['name'],
         'company_id': result['company_id']
      }
      
      return vals
  
   @http.route('/create_opportunity', type='json', auth='public')
   def create_opportunity(self,**kwargs):
      state_id= '597'
      country_id='104'
      login = request.env['ir.http'].session_info()
#       print('>>>>>>>>>>>>>>Login',login)
      current_uid= login['uid']
#       print('>>>>>>>>>>>>>>Login',stage_id)
      
      # for data in kwargs:
        
      if (kwargs['stage_id']=='Qualified'):
            kwargs['stage_id']= 2
      if (kwargs['stage_id']=='Proposition'):
            kwargs['stage_id']= 3
      if (kwargs['stage_id']=='Won'):
            kwargs['stage_id']= 4
      if (kwargs['stage_id']=='New'):
            kwargs['stage_id']= 1
            
      if (kwargs['patner_id']):
        print("partner_id>>>>>>>>>>>>>>>>>",kwargs['patner_id'])
        kwargs['partner_id']=request.env['res.partner'].sudo().search([("name", "=",kwargs['patner_id'])])
        print("partner_id>>>>>>>>>>>>>>>>>",kwargs['patner_id'])
            
      record_status = request.env['crm.lead'].sudo().create(

         {
            "name": kwargs['name'],
#             "contact_name":kwargs['contact_name'],
            "partner_id":request.env['res.partner'].sudo().search([("name", "=",kwargs['patner_id'])]),
            
            "street":kwargs['street'],
            "street2":kwargs['street2'],
            "city":kwargs['city'],
            "zip":kwargs['zip'],
            "state_id":state_id,
            "country_id":104,
            "email_from": kwargs['email_from'],
            "phone": kwargs['phone'],
            "mobile":kwargs['mobile'],
            "website":kwargs['website'],
            "stage_id":kwargs['stage_id'],
            "user_id":request.env['res.users'].browse(current_uid),
            "type":'opportunity',
#             "stage_id":kwargs['stage_id']['id'],
            
           
         }
         
         
      
      )
      print(record_status)
      return "Status Creation Successfully Done"

   # @http.route('/web/session/authenticate/test', type='json', auth="none", withCredentials= 'true')
   # def authenticate(self, db, login, password, base_location=None):
   #    request.session.authenticate(db, login, password)
   #    record = request.env['ir.http'].session_info()
   #    vals={
         
   #       'uid': record['uid'],
   #       'name': record['name'],
   #       'company_id': record['company_id']
   #    }
      
   #    return 'Status: Successful'


   # @http.route('/update_cust', type='json', auth='public')
   # def update_customer(self,**kwargs):
      
   #    for data in kwargs:
   #       record_status = request.env['res.partner'].sudo().search([("id", "=",kwargs['id'])]).write(kwargs)
   #       print(kwargs)
   #       return "Status Creation Successfully Done"
   
   @http.route('/lead/mark_won', type='json', auth='public')
   def crm_lead_mark_won(self,**kwargs):
      
      for data in kwargs:
         lead=request.env['crm.lead']
         print('>>>>>>>>>',lead)
         stage_id = lead._stage_find(domain=[('is_won', '=', True)])
         record_status = request.env['crm.lead'].sudo().search([("id", "=",kwargs['id'])]).write(
            {  
               'stage_id': stage_id.id, 
               'probability': 100
               })
         return 'Status: Successful'
   
   @http.route('/mark_loss', type='json', auth='public')
   def crm_lead_mark_loss(self,**kwargs):
      for data in kwargs:
         lead=request.env['crm.lead']

         record_status = request.env['crm.lead'].sudo().search([("id", "=",kwargs['id'])]).write(
            {  
             'active': False, 
             'probability': 0,
             'automated_probability': 0,
             }
            )
         return 'Status: Successful'

   @http.route('/convert_opportunity', type='json', auth='public')
   def convert_opportunity(self,**kwargs):
      team_id=False
      lead_rec = request.env['crm.lead'].sudo().search([("id", "=",kwargs['id'])])
      partner=request.env['res.partner']
      records =[]
      

      for rec in lead_rec:
         vals= {
#                "partner_id":rec.partner_id.name,
               "user_id":rec.user_id,
               "name":rec.name}

#          if (vals["partner_id"]):
#             customer = (vals["partner_id"])
#             print(customer)
            
         if (rec.contact_name)== partner.name:
            partner_id = (vals["contact_name"])
            print('>>>>>>>>>>>>>>>>>>>=======is existing:')
            
         if (rec.contact_name)!= partner.name:
                record_status = request.env['res.partner'].sudo().create({
                    "name": rec.contact_name,
                     "state_id":597,
                     "country_id":104,})
                print('>>>>>>>>>>>>>>>>>>>id:',(record_status["id"]))
                cust_id = (record_status["id"])
#                 (vals["partner_id"])==cust_id
                    
               
                
         
         if (vals["user_id"]):
            user_ids = (vals["user_id"])
            print(user_ids)
         if (vals["name"]):
            name = (vals["name"])
            print(name)
     
      
      for data in kwargs:
         lead=request.env['crm.lead'].sudo().search([("id", "=",kwargs['id'])])
         customer=lead.partner_id

         
         # vals = lead._convert_opportunity_data(team_id)
         record_status = request.env['crm.lead'].sudo().search([("id", "=",kwargs['id'])]).write(
            {
            'planned_revenue': lead.planned_revenue,
            'probability': lead.probability,
            'name': lead.name,
            'partner_id': cust_id,
            'type': 'opportunity',
            'date_open': fields.Datetime.now(),
            'email_from': customer and customer.email or lead.email_from,
            'phone': customer and customer.phone or lead.phone,
            'date_conversion': fields.Datetime.now(),
            }


         )
#          if user_ids:
#             lead.allocate_salesman(user_ids)
         return 'Successful'
   

   @http.route('/create_cust', type='json', auth='public')
   def create_customer(self,**kwargs):
      
      # for data in kwargs:
         print(kwargs)
         record_status = request.env['res.partner'].sudo().create(

            {
               "name": kwargs['name'],
               "street":kwargs['street'],
               "street2":kwargs['street2'],
               "city":kwargs['city'],
               "zip":kwargs['zip'],
               "state_id":kwargs['state_id'],
               "country_id":104,
               "email": kwargs['email'],
               "phone": kwargs['phone'],
               "mobile":kwargs['mobile']
            }

         )
         return "Status Creation Successfully Done"
     
    
   @http.route('/create_company', type='json', auth='public')
   def create_company(self,**kwargs):
      
      # for data in kwargs:
         print(kwargs)
         record_status = request.env['res.partner'].sudo().create(

            {
                "company_type":'company',
               "name": kwargs['name'],
               "street":kwargs['street'],
               "street2":kwargs['street2'],
               "city":kwargs['city'],
               "zip":kwargs['zip'],
               "state_id":kwargs['state_id'],
               "country_id":104,
               "email": kwargs['email'],
               "phone": kwargs['phone'],
               "mobile":kwargs['mobile']
            }

         )
         return "Status Creation Successfully Done"
   
   @http.route('/get_cust', type='json', auth='public')
   def get_customer(self):
      customer_rec = request.env['res.partner'].sudo().search([])
      customers =[]

      for rec in customer_rec:
            
         vals= {
               "id":rec.id,
               "name":rec.name,
               "street":rec.street,
               "street2":rec.street2,
               "city":rec.city,
               "zip":rec.zip,
               "state_id":rec.state_id.name,
               "country_id":rec.country_id.name,
               "email": rec.email,
               "phone":rec.phone,
               "mobile":rec.mobile
            } 

         if (vals["street"] == False):
            
            vals["street"] = ""
         if (vals["street2"] == False):
            vals["street2"] = ""
         if (vals["city"] == False):
            vals["city"] = ""
         if (vals["state_id"] == False):
            vals["state_id"] = ""
         if (vals["country_id"] == False):
            vals["country_id"] = ""
         if (vals["zip"] == False):
            vals["zip"] = ""
         if (vals["email"] == False):
            vals["email"] = ""
         if (vals["phone"] == False):
            vals["phone"] = ""
         if (vals["mobile"] == False):
            vals["mobile"] = ""

         customers.append(vals)
         print('>>>>>>>>>>>>>>>>>>',customer_rec)

      return customers
  
   @http.route('/get_company', type='json', auth='public')
   def get_company(self):
      customer_rec = request.env['res.partner'].sudo().search([('is_company', '=', 'true')])
      customers =[]

      for rec in customer_rec:
            
         vals= {
               "id":rec.id,
               "name":rec.name,
               "street":rec.street,
               "street2":rec.street2,
               "city":rec.city,
               "zip":rec.zip,
               "state_id":rec.state_id.name,
               "country_id":rec.country_id.name,
               "email": rec.email,
               "phone":rec.phone,
               "mobile":rec.mobile
            } 

         if (vals["street"] == False):
            
            vals["street"] = ""
         if (vals["street2"] == False):
            vals["street2"] = ""
         if (vals["city"] == False):
            vals["city"] = ""
         if (vals["state_id"] == False):
            vals["state_id"] = ""
         if (vals["country_id"] == False):
            vals["country_id"] = ""
         if (vals["zip"] == False):
            vals["zip"] = ""
         if (vals["email"] == False):
            vals["email"] = ""
         if (vals["phone"] == False):
            vals["phone"] = ""
         if (vals["mobile"] == False):
            vals["mobile"] = ""

         customers.append(vals)
         print('>>>>>>>>>>>>>>>>>>',customer_rec)

      return customers
  
  

   @http.route('/update_lead', type='json', auth='public')
   def update_lead(self,**rec):
    opportunity = request.env['crm.lead'].sudo().search([("id", "=",rec['id'])])
    
    if opportunity['type']== 'opportunity':
        
        if (rec['stage_id']=='Qualified'):
            print('>>>>>>>>>>>>STAGE ID:',rec['stage_id'])
            rec['stage_id']= 2
        if (rec['stage_id']=='Proposition'):
            print('>>>>>>>>>>>>STAGE ID:',rec['stage_id'])
            rec['stage_id']= 3
        if (rec['stage_id']=='Won'):
            print('>>>>>>>>>>>>STAGE ID:',rec['stage_id'])
            rec['stage_id']= 4
            print('>>>>>>>>>>>>STAGE ID:',rec['stage_id'])
        if (rec['stage_id']=='New'):
            print('>>>>>>>>>>>>STAGE ID:',rec['stage_id'])
            rec['stage_id']= 1
        if opportunity:
            opportunity.sudo().write(rec)
        return 'Status: Successful'
    
    if opportunity['type']== 'lead':
        if opportunity:
            opportunity.sudo().write(rec)
        return 'Status: Successful'
            
        
            
    
              
              
#      

#       if opportunity:
#           opportunity.sudo().write(rec)
      
          
                          
                      
#                       print ('>>>>>>>>>>>>>>',vals)
                          
#                           return "Status Successfully Done"
                      
                        
                        
      
      
   
   @http.route('/create_lead', type='json', auth='public')
   def create_lead(self,**kwargs):
      state_id= '597'
      country_id='104'
      login = request.env['ir.http'].session_info()
      print('>>>>>>>>>>>>>>Login',login)
      current_uid= login['uid']
      
      # for data in kwargs:
            
      record_status = request.env['crm.lead'].sudo().create(

         {
            "name": kwargs['name'],
            "contact_name":kwargs['contact_name'],
            "street":kwargs['street'],
            "street2":kwargs['street2'],
            "city":kwargs['city'],
            "zip":kwargs['zip'],
            "state_id":state_id,
            "country_id":104,
            "email_from": kwargs['email_from'],
            "phone": kwargs['phone'],
            "mobile":kwargs['mobile'],
            "website":kwargs['website'],
            "user_id":request.env['res.users'].browse(current_uid),
            "type":'lead',
         }
      
      )
      print(record_status)
      return "Status Creation Successfully Done"
  
  

   
   
   @http.route('/get_lead', type='json', auth='public')
   def get_lead(self):
      lead_rec = request.env['crm.lead'].sudo().search([('type', '=', 'lead')])
      records =[]
      

      for rec in lead_rec:
  
         vals= {
               "id":rec.id,
               "partner_id":rec.partner_id.name,
               "contact_name":rec.contact_name,
               "name":rec.name,
               "street":rec.street,
               "street2":rec.street2,
               "city":rec.city,
               "zip":rec.zip,
               "state_id":rec.state_id.name,
               "country_id":rec.country_id.name,
               "email_from": rec.email_from,
               "phone":rec.phone,
               "mobile":rec.mobile,
               "salesperson":rec.user_id,
               "website":rec.website,
               "type":rec.type,
               "stage_id":rec.stage_id.name
            }
         if (vals["contact_name"] == False):
            vals["contact_name"] = ""
         if (vals["partner_id"] == False):
            vals["partner_id"] = ""
         if (vals["name"] == False):
            vals["name"] = ""
         if (vals["street"] == False):
            vals["street"] = ""
         if (vals["street2"] == False):
            vals["street2"] = ""
         if (vals["city"] == False):
            vals["city"] = ""
         if (vals["zip"] == False):
            vals["zip"] = ""
         if (vals["state_id"] == False):
            vals["state_id"] = ""
         if (vals["country_id"] == False):
            vals["country_id"] = ""
         if (vals["email_from"] == False):
            vals["email_from"] = ""
         if (vals["phone"] == False):
            vals["phone"] = ""
         if (vals["mobile"] == False):
            vals["mobile"] = ""
         if (vals["salesperson"] == False):
            vals["salesperson"] = ""
         if (vals["website"] == False):
            vals["website"] = ""

        
         records.append(vals)
      return records

    
   @http.route('/get_oppo', type='json', auth='public')
   def get_oppo(self):
      lead_rec = request.env['crm.lead'].sudo().search([('type', '=', 'opportunity')])
      records =[]
      

      for rec in lead_rec:
  
         vals= {
               "id":rec.id,
               "partner_id":rec.partner_id.name,
#                "contact_name":rec.contact_name,
               "name":rec.name,
               "street":rec.street,
               "street2":rec.street2,
               "city":rec.city,
               "zip":rec.zip,
               "state_id":rec.state_id.name,
               "country_id":rec.country_id.name,
               "email_from": rec.email_from,
               "phone":rec.phone,
               "mobile":rec.mobile,
               "salesperson":rec.user_id,
               "website":rec.website,
               "type":rec.type,
               "stage_id":rec.stage_id.name
            }
         if (vals["partner_id"] == False):
            vals["partner_id"] = ""
         if (vals["name"] == False):
            vals["name"] = ""
         if (vals["street"] == False):
            vals["street"] = ""
         if (vals["street2"] == False):
            vals["street2"] = ""
         if (vals["city"] == False):
            vals["city"] = ""
         if (vals["zip"] == False):
            vals["zip"] = ""
         if (vals["state_id"] == False):
            vals["state_id"] = ""
         if (vals["country_id"] == False):
            vals["country_id"] = ""
         if (vals["email_from"] == False):
            vals["email_from"] = ""
         if (vals["phone"] == False):
            vals["phone"] = ""
         if (vals["mobile"] == False):
            vals["mobile"] = ""
         if (vals["salesperson"] == False):
            vals["salesperson"] = ""
         if (vals["website"] == False):
            vals["website"] = ""
         if (vals["stage_id"] == False):
            vals["stage_id"] = ""

        
         records.append(vals)
      return records

#    @http.route('/get_opportunity', type='json', auth='public')
#    def get_oppoertunity(self):
#       lead_rec = request.env['crm.lead'].sudo().search([('type', '=', 'opportunity')])
#       records =[]
#       
# 
#       for rec in lead_rec:
#             
#          vals= {
#                "id":rec.id,
#                "partner_id":rec.partner_id.name,
#                "name":rec.name,
#                "street":rec.street,
#                "street2":rec.street2,
#                "city":rec.city,
#                "zip":rec.zip,
#                "state_id":rec.state_id.name,
#                "country_id":rec.country_id.name,
#                "email_from": rec.email_from,
#                "phone":rec.phone,
#                "mobile":rec.mobile,
#                "salesperson":rec.user_id.name,
#                "website":rec.website,
#                "type":rec.type,
#                "stage_id":rec.stage_id.name
#             }
#          if (vals["partner_id"] == False):
#             vals["partner_id"] = ""
#          if (vals["name"] == False):
#             vals["name"] = ""
#          if (vals["street"] == False):
#             vals["street"] = ""
#          if (vals["street2"] == False):
#             vals["street2"] = ""
#          if (vals["city"] == False):
#             vals["city"] = ""
#          if (vals["zip"] == False):
#             vals["zip"] = ""
#          if (vals["state_id"] == False):
#             vals["state_id"] = ""
#          if (vals["country_id"] == False):
#             vals["country_id"] = ""
#          if (vals["email_from"] == False):
#             vals["email_from"] = ""
#          if (vals["phone"] == False):
#             vals["phone"] = ""
#          if (vals["mobile"] == False):
#             vals["mobile"] = ""
#          if (vals["salesperson"] == False):
#             vals["salesperson"] = ""
#          if (vals["website"] == False):
#             vals["website"] = ""
#          
#          records.append(vals)
#       return records


   @http.route('/get_country', type='json', auth='public')
   def get_country(self):
      country_rec = request.env['res.country'].sudo().search([])
      country =[]

      for rec in country_rec:
             
         vals= {
               "id":rec.id,
               "name":rec.name,
               
            }
         # print(vals)
         country.append(vals)


      return country

   @http.route('/get_stage', type='json', auth='public')
   def get_stages(self):
      lead_rec = request.env['crm.stage'].sudo().search([])
      stage =[]

      for rec in lead_rec:
           
         vals= {
               "id":rec.id,
               "name":rec.name
               
            }
         # print(vals) 
         stage.append(vals)


      return stage
   
   @http.route('/get_state', type='json', auth='public')
   def get_states(self):
      states_rec = request.env['res.country.state'].sudo().search([('country_id', '=', 104)])
      state =[]

      for rec in states_rec:
           
         vals= {
               "id":rec.id,
               "name":rec.name,
               
            }
         # print(vals) 
         state.append(vals)


      return state

   @http.route('/update_cust', type='json', auth='public')
   def update_customer(self, **rec):
      if request.jsonrequest:
         if rec['id']:
               print("rec...", rec)
               patient = request.env['res.partner'].sudo().search([('id', '=', rec['id'])])
               if (rec["state_id"] == '' or 'Select State'):
               # if rec['state_id']=''
                  state_id= '597'
                  print(state_id)
                  rec['state_id']= 597
               if (rec["country_id"] == '' or 'Select Country'):
                  country_id= '104'
                  print(country_id)
                  rec['country_id']= 104
               if patient:
                  patient.sudo().write(rec)
               args = {'success': True, 'message': 'Customer Updated'}
      return "Status Updataion of record Successfully Done"
  
   @http.route('/update_company', type='json', auth='public')
   def update_company(self, **rec):
      if request.jsonrequest:
         if rec['id']:
               print("rec...", rec)
               patient = request.env['res.partner'].sudo().search([('id', '=', rec['id'])])
               if (rec["state_id"] == '' or 'Select State'):
               # if rec['state_id']=''
                  state_id= '597'
                  is_company=true
                  print(state_id)
                  rec['state_id']= 597
               if (rec["country_id"] == '' or 'Select Country'):
                  country_id= '104'
                  print(country_id)
                  rec['country_id']= 104
               if patient:
                  patient.sudo().write(rec)
               args = {'success': True, 'message': 'Customer Updated'}
      return "Status Updataion of record Successfully Done"
  
   @http.route('/update_cal', type='json', auth='public')
   def update_cal(self, **rec):
      if request.jsonrequest:
               print("rec...", rec)
               meeting = request.env['calendar.event'].sudo().search([('id', '=', rec['id'])])
               if rec["start"]:
                   start=datetime.strptime(rec["start"], "%Y-%m-%d %H:%M:%S")
                   
                   start= start.astimezone(pytz.utc)
                   start=start- timedelta(hours=5,minutes=30)
                   print(">>>>>>>>>>>>>>stop Here >>>>>>>>>>>>>>>>>>>>",start)
                   rec["start"]=start.strftime("%Y-%m-%d %H:%M:%S")[:19]
                   
                   print(">>>>>>>>>>>>>>start Here >>>>>>>>>>>>>>>>>>>>",rec["start"])
                   
               if rec["stop"]:
                   stop=datetime.strptime(rec["stop"], "%Y-%m-%d %H:%M:%S")
                   
                   stop= stop.astimezone(pytz.utc)
                   stop=stop- timedelta(hours=5,minutes=30)
                   
                   print(">>>>>>>>>>>>>>stop Here >>>>>>>>>>>>>>>>>>>>",stop)
                   
                   rec["stop"]=stop.strftime("%Y-%m-%d %H:%M:%S")[:19]
                   print(">>>>>>>>>>>>>>stop Here >>>>>>>>>>>>>>>>>>>>",rec["stop"])
                   
                   
               if rec["partner_ids"]:
                  partner_ids=rec['partner_ids']
                  rec['partner_ids']= request.env['res.partner'].sudo().browse(int(partner_id) for partner_id in partner_ids)
                  meeting.sudo().write(rec)
               args = {'success': True, 'message': 'Meeting Updated Successfully'}
      return "Status Updataion of record Successfully Done"
  
  
  
  
   
   @http.route('/get_customer', type='json', auth='public')
   def get_cust(self):
      cust_rec = request.env['res.partner'].sudo().search([])
      cust =[]

      for rec in cust_rec:
            
         vals= {
               "id":rec.id,
               "name":rec.name,
               
            }
         cust.append(vals)


      return cust
  
   



   @http.route('/create_calendar', type='json', auth='public')
   def create_calendar(self,**kwargs):
       
       
    record_status = request.env['calendar.event'].sudo().create(
        {
           "name":kwargs['name'],
           "start":kwargs['start'],
            "stop":kwargs['stop'],
        }
     )
    partner_ids=kwargs['partner_ids']
#     print(">>>>>>>>>>>>>>kwargs['partner_ids']>>>>>>>>>>>>>>>>>>>>",kwargs['partner_ids'])
#     print(">>>>>>>>>>>>>>partner_ids>>>>>>>>>>>>>>>>>>>>",partner_ids)
    meeting = request.env['calendar.event'].sudo().search([('id', '=', record_status.id)])
    
#     start=meeting.start
#     stop=meeting.stop
    
    start=datetime.strptime(kwargs['start'], "%Y-%m-%d %H:%M:%S")
    stop=datetime.strptime(kwargs['stop'], "%Y-%m-%d %H:%M:%S")
    
    user_tz=pytz.timezone('Asia/Kolkata')
    
    print(">>>>>>>>>>>>>>Time Zone Here >>>>>>>>>>>>>>>>>>>>",user_tz)
    
    start= start.astimezone(pytz.utc)
    stop= stop.astimezone(pytz.utc)
    
    start=start- timedelta(hours=5,minutes=30)
    stop=stop- timedelta(hours=5,minutes=30)
    
    start=start.strftime("%Y-%m-%d %H:%M:%S")[:19]
    stop=stop.strftime("%Y-%m-%d %H:%M:%S")[:19]
    

#     start=str(start)[:19]
#     stop=str(stop)[:19]

    print(">>>>>>>>>>>>>>Start Time Here>>>>>>>>>>>>>>>>>>>>",start) 
    print(">>>>>>>>>>>>>>stop Time Here >>>>>>>>>>>>>>>>>>>>",stop) 
#     print(">>>>>>>>>>>>>>stop Time Here >>>>>>>>>>>>>>>>>>>>",duration) 
    
    
    meeting.sudo().write(
            {
    'partner_ids': request.env['res.partner'].sudo().browse(int(partner_id) for partner_id in partner_ids),
    'start':start,
    'stop':stop,
#     'duration':duration
            }
            )
    
#     if kwargs['start']:
#         user_tz= pytz.timezone(request.env.context.get('tz') or request.env.user.tz)
#         print(">>>>>>>>>>>>>>Start Time>>>>>>>>>>>>>>>>>>>>",user_tz)
#         kwargs['start']= pytz.utc.localize(kwargs['start']).astimezone(user_tz)
#         print(">>>>>>>>>>>>>>Start Time>>>>>>>>>>>>>>>>>>>>",kwargs['start'])
    
    return "Successful"
     
   
   @http.route('/get_calendar', type='json', auth='public')
   def get_calendar(self):
      cal_rec = request.env['calendar.event'].sudo().search([])
      cals = []
#       attendees=[]
      
      
              
           

      for rec in cal_rec:
            
         vals= {
               "id":rec.id,
               "name":rec.name,
               "start":rec.start,
               "stop":rec.stop,
               "partner_ids":rec.partner_ids,
               "location":rec.location,
               "duration":rec.duration,
              
            }
         all_cust_ids=[]
         all_cust_names=[]
         
         cust_ids=vals['partner_ids']
         attendees=request.env['res.partner']
         attendees= attendees.sudo().browse(str(partner_id.name) for partner_id in cust_ids)
         attendees1= attendees.sudo().browse(int(partner_id) for partner_id in cust_ids)
         for attendee in attendees1:
             all_cust_ids.append(attendee.name)
             
             all_cust_ids1=list(map(str,all_cust_ids))
             attendees=','.join(map(str, all_cust_ids1))
             
         
#          print(">>>>>>>>>>>>>>partner_ids>>>>>>>>>>>>>>>>>>>>",attendees)

         
         start=datetime.strptime(str(rec.start), "%Y-%m-%d %H:%M:%S")
         print(">>>>>>>>>>>>>>start Here >>>>>>>>>>>>>>>>>>>>",start)
         stop=datetime.strptime(str(rec.stop), "%Y-%m-%d %H:%M:%S")
        
         user_tz=pytz.timezone('Asia/Kolkata')
        
#          print(">>>>>>>>>>>>>>Time Zone Here >>>>>>>>>>>>>>>>>>>>",user_tz)
        
         start= pytz.utc.localize(start).astimezone(user_tz)
         stop= pytz.utc.localize(stop).astimezone(user_tz)
         start=start.strftime("%Y-%m-%d %H:%M:%S")[:19]
         stop=stop.strftime("%Y-%m-%d %H:%M:%S")[:19]
         
         date_value=rec.start.date()
         today = datetime.now().date()
         
         print('>>>>>>>>>>>>>>>>>>>>>Date :<>>>>>>>>>>', date_value)
         print('>>>>>>>>>>>>>>>>>>>>>Date :<>>>>>>>>>>', today)
         
         
             
         vals= {
               "id":rec.id,
               "name":rec.name,
               "start":start,
               "stop":stop,
               "partner_ids":rec.partner_ids,
               "location":rec.location,
               "duration":rec.duration,
                "attendees":attendees,
                "new": False,
                "time":'next'
              
            }
         
         if (date_value == today):
            vals["time"] = "today"
            
         if (date_value < today):
            vals["time"] = "done"
        
         
         if (vals["location"] == False):
            vals["location"] = ""
            
         if (vals["partner_ids"]):
            partner = list(map(int, vals["partner_ids"]))
             
            vals["partner_ids"]=list(map(str, partner))
            vals["partner_ids"]=','.join(map(str, partner))
         
#          if (vals["new"] == False):

            
         cals.append(vals)

      return cals
  
#    @http.route('/get_partner', type='json', auth='public')
#    def get_attendees(self):
#       cust_rec = request.env['res.partner'].sudo().search([])
#       cust =[]
#       
#       
# 
#       for rec in cust_rec:
#             
#          vals= {
#                 "checked":False,
#                "id":rec.id,
#                "name":rec.name,
#                
#             }
#          cust.append(vals)
# 
# 
#       return cust
   @http.route('/get_partner', type='json', auth='public')
   def get_attendees(self,**kwargs):
       
      cal_rec = request.env['calendar.event'].sudo().search([('id', '=', kwargs['id'])])
      
      cal_rec=cal_rec.partner_ids
      cal_rec = list(map(int, cal_rec))
             
      cal_rec=list(map(str, cal_rec))
      cal_rec=list(map(int, cal_rec))
      cust_rec = request.env['res.partner'].sudo().search([])
      cust =[]
      
      

      for rec in cust_rec:
            
         vals= {
                "checked":False,
               "id":rec.id,
               "name":rec.name,
               
            }
         
         for record in cal_rec:
             
             value=rec.id
             if value == record:
                vals["checked"]=True
                
                
         cust.append(vals)
         

      return cust
   


   






    
   #  @http.route('/post/data', type='http', auth='public',methods=["POST"], website=False, csrf=False)
   #  def get_data(self,**kwargs):
        
   #     http = urllib3.PoolManager()
   #     URL = 'http://localhost:9930'
   #     root = '/post/data'  
   #     datas = http.request('POST', URL+root)
   #     name='admin'
   #     password='admin'
       
   #     if (kwargs['user'] == name) and (kwargs['password'] == password):
   #          for data in kwargs:
   #             record_status = request.env['test.api'].sudo().create(kwargs)
   #             return '{****** Status: Creation Successfully Done ******}'
   #     return '{Status: Username and password invalid}'
           
           
    
   #  @http.route('/update/data', type='http', auth='public',methods=["POST"], website=False, csrf=False)
   #  def update_data(self,**kwargs):
         
   #     http = urllib3.PoolManager()
   #     URL = 'http://localhost:9930'
   #     root = '/update/data'  
   #     datas = http.request('POST', URL+root)
   #     email='admin'
   #     password='admin'
   #     id=47
        
   #     if (kwargs['user'] == email) and (kwargs['password'] == password):
   #          for data in kwargs:
   #             record_status = request.env['test.api'].browse(id).sudo().write({
   #                 'street':kwargs['street']
   #                 })
   #             return '{****** Status: Creation Successfully Done ******}'
   #     return '{Status: Username and password invalid}'  
      
    
    
    
   #  @http.route('/update/cust', type='http', auth='public',methods=["POST"], website=False, csrf=False)
   #  def update_customer(self,**kwargs):
        
   #     http = urllib3.PoolManager()
   #     URL = 'http://localhost:9930'
   #     root = '/update/data'  
   #     datas = http.request('POST', URL+root)
   #     email='admin'
   #     password='admin'
       
   #     if (kwargs['user'] == email) and (kwargs['password'] == password):
   #          id=(kwargs['id'])
   #          cust = request.env['res.partner'].search((kwargs['id']), limit=1)
   #          print('>>>>>>>>>>>>>>>>>>>>>>>',cust)
   #          id= cust
   #          print('>>>>>>>>>>>>>>>>>>>>>>>',id)
   #          for data in kwargs:
   #             record_status = request.env['res.partner'].search(id).write({
   #                 'previous_month':kwargs['previous_month']
   #                 })
   #             return '{****** Status: upfate Successfully Done ******}'
   #     return '{Status: Username and password invalid}'  
    
      
      
      
      
      
      
 