from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models.account import Account
import qrcode
import io
import uuid

qrcode_bp = Blueprint('qrcode', __name__)

@qrcode_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_qr_code():
    """
    Generate QR code for payment
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('account_id') or not data.get('amount'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    account = Account.query.filter_by(id=data['account_id'], user_id=current_user_id).first()
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    amount = float(data['amount'])
    reference = data.get('reference', f"PAY{uuid.uuid4().hex[:8].upper()}")
    
    qr_data = f"payment://{account.account_number}/{amount}/{reference}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f'{reference}.png')

@qrcode_bp.route('/decode', methods=['POST'])
@jwt_required()
def decode_qr_code():
    """
    Decode QR code for payment
    """
    data = request.get_json()
    
    if not data.get('qr_data'):
        return jsonify({'error': 'Missing QR data'}), 400
    
    qr_data = data['qr_data']
    
    try:
        if qr_data.startswith('payment://'):
            parts = qr_data.replace('payment://', '').split('/')
            if len(parts) != 3:
                return jsonify({'error': 'Invalid QR format'}), 400
            
            account_number, amount, reference = parts
            
            return jsonify({
                'account_number': account_number,
                'amount': float(amount),
                'reference': reference
            }), 200
        else:
            return jsonify({'error': 'Invalid QR format'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to decode QR: {str(e)}'}), 400